import fcntl
import os
from pathlib import Path


class Lock:
    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def acquire(self):
        flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW

        try:
            fd = os.open(self.path, flags, 0o644)
        except OSError as exc:
            raise RuntimeError(f'failed to open instance lock: {self.path}') from exc

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(fd)
            raise RuntimeError('another mwan instance is already running') from exc
        except OSError:
            os.close(fd)
            raise

        try:
            os.ftruncate(fd, 0)
            os.write(fd, f'{os.getpid()}\n'.encode())
        except OSError as exc:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            raise RuntimeError(f'failed to update instance lock: {self.path}') from exc
        self.fd = fd

    def release(self):
        if self.fd is None:
            return

        fd = self.fd
        self.fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.release()

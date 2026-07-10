import subprocess


def cmd(
    command: list[str], *, timeout: int | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

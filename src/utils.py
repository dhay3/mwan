import subprocess


def cmd(
    command: list[str], *, timeout: int | None = 5
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

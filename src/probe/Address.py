import socket


def resolve_ipv4(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except OSError as exc:
        raise ValueError(f"invalid host: {host}") from exc

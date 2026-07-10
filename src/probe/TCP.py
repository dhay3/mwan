from functools import cache
from typing import NamedTuple

from config.Config import MwanConfig


class ScapyTCPModules(NamedTuple):
    IP: type
    TCP: type
    send: object
    sr1: object


@cache
def load_scapy() -> ScapyTCPModules:
    try:
        from scapy.layers.inet import IP, TCP
        from scapy.sendrecv import send, sr1
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "scapy is required for TCP probe packets; install scapy>=2.6,<3.0"
        ) from exc
    return ScapyTCPModules(IP, TCP, send, sr1)


def parse_host_port(value: str) -> tuple[str, int]:
    host, separator, port_value = value.rpartition(":")
    if not separator or not host or not port_value:
        raise ValueError(f"tcp host must include port: {value}")

    try:
        port = int(port_value)
    except ValueError as exc:
        raise ValueError(f"invalid port in host: {value}") from exc

    if port < 1 or port > 65535:
        raise ValueError(f"port out of range in host: {value}")

    return host, port


def ping(config: MwanConfig, addr: str) -> bool:
    host, port = parse_host_port(addr)
    scapy = load_scapy()

    for _ in range(config.probe.count):
        packet = scapy.IP(dst=host) / scapy.TCP(dport=port, flags="S")
        response = scapy.sr1(
            packet,
            iface=config.primary.dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if not response or not response.haslayer(scapy.TCP):
            continue

        tcp = response.getlayer(scapy.TCP)
        if tcp.flags & 0x12 == 0x12:
            reset = scapy.IP(dst=host) / scapy.TCP(
                dport=port,
                sport=tcp.dport,
                flags="R",
                seq=tcp.ack,
            )
            scapy.send(reset, iface=config.primary.dev, verbose=False)
            return True
    return False

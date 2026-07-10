from functools import cache
from typing import NamedTuple

from config.Config import MwanConfig


class ScapyICMPModules(NamedTuple):
    ICMP: type
    IP: type
    sr1: object


@cache
def load_scapy() -> ScapyICMPModules:
    try:
        from scapy.layers.inet import ICMP, IP
        from scapy.sendrecv import sr1
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "scapy is required for ICMP probe packets; install scapy>=2.6,<3.0"
        ) from exc
    return ScapyICMPModules(ICMP, IP, sr1)


def ping(config: MwanConfig, host: str) -> bool:
    if ":" in host:
        raise ValueError(f"icmp host must not include port: {host}")

    scapy = load_scapy()
    for sequence in range(config.probe.count):
        packet = scapy.IP(dst=host) / scapy.ICMP(seq=sequence)
        response = scapy.sr1(
            packet,
            iface=config.primary.dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if response and response.haslayer(scapy.ICMP):
            icmp = response.getlayer(scapy.ICMP)
            if icmp.type == 0:
                return True
    return False

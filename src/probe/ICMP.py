import socket

from config import MwanConfig

from scapy.all import (
    ICMP,
    IP,
    sr1,
)


def ping(config: MwanConfig, addr: str):
    scope_addr = f"{socket.gethostbyname(addr)}%{config.primary.dev}"
    for _ in range(config.probe.count):
        packet = IP(dst=scope_addr) / ICMP(seq=_)
        ans = sr1(
            packet,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(ICMP):
            icmp = ans.getlayer(ICMP)
            if icmp.type == 0:
                return True
    return False

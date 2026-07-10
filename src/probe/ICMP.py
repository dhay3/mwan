from config import MwanConfig
from scapy.all import (
    sr1,
    ICMP,
    IP,
)


def ping(config: MwanConfig, addr: str):
    for _ in range(config.probe.count):
        packet = IP(dst=addr) / ICMP(seq=_)
        ans = sr1(
            packet,
            iface=config.primary.dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(ICMP):
            icmp = ans.getlayer(ICMP)
            if icmp.type == 0:
                return True
    return False

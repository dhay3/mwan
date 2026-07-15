import socket


from config import MwanConfig

from scapy.all import (
    Ether,
    ICMP,
    IP,
    srp1,
    get_if_hwaddr,
    get_if_addr,
    arping,
)


def ping(config: MwanConfig, addr: str):
    dev = config.primary.dev
    dst_addr = socket.gethostbyname(addr)
    for _ in range(config.probe.count):
        packet = (
            Ether(src=get_if_hwaddr(dev), dst=arping(dst_addr))
            / IP(src=get_if_addr(dev), dst=dst_addr)
            / ICMP()
        )
        ans = srp1(
            packet,
            iface=dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(ICMP):
            icmp = ans.getlayer(ICMP)
            if icmp.type == 0:
                return True
    return False

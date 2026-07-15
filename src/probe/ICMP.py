import socket

from config import MwanConfig
from scapy.all import (
    Ether,
    ICMP,
    IP,
    get_if_addr,
    get_if_hwaddr,
    srp1,
)

from .ARP import arp_request, get_hwsrc


def ping(config: MwanConfig, addr: str):
    dev = config.primary.dev
    dst_addr = socket.gethostbyname(addr)
    src_addr = get_if_addr(dev)
    src_hwaddr = get_if_hwaddr(dev)
    dst_hwaddr = get_hwsrc(arp_request(src_addr, dst_addr, dev, config.probe.timeout))
    for _ in range(config.probe.count):
        packet = (
            Ether(
                src=src_hwaddr,
                dst=dst_hwaddr,
            )
            / IP(src=src_addr, dst=dst_addr)
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

from config.Config import MwanConfig
from scapy.all import (
    Ether,
    IP,
    TCP,
    get_if_addr,
    get_if_hwaddr,
    sendp,
    srp1,
)

from .ARP import resolve_hwaddr
from .DNS import resolve_host


def ping(config: MwanConfig, addr: str):
    host, port = addr.split(':', maxsplit=1)
    port = int(port)
    dev = config.primary.dev
    dst_addr = resolve_host(config, host)
    src_addr = get_if_addr(dev)
    src_hwaddr = get_if_hwaddr(dev)
    dst_hwaddr = resolve_hwaddr(src_addr, dst_addr, dev, config.probe.timeout)

    for _ in range(config.probe.count):
        packet = (
            Ether(src=src_hwaddr, dst=dst_hwaddr)
            / IP(src=src_addr, dst=dst_addr)
            / TCP(dport=port, flags='S')
        )
        ans = srp1(
            packet,
            iface=dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(TCP):
            l3 = ans.getlayer(TCP)
            if l3.flags & 0x12 == 0x12:
                packet = (
                    Ether(src=src_hwaddr, dst=dst_hwaddr)
                    / IP(src=src_addr, dst=dst_addr)
                    / TCP(
                        dport=port,
                        sport=l3.dport,
                        flags='R',
                        seq=l3.ack,
                    )
                )
                sendp(
                    packet,
                    iface=dev,
                    verbose=False,
                )
                return True
    return False

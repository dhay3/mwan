from scapy.all import (
    ARP,
    Ether,
    srp1,
)

from route.Route import get_route


def arp_request(src: str, dst: str, dev: str, timeout: int):
    route = get_route(dst, ['from', src, 'oif', dev])
    next_hop = route.gateway or dst
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(
        op='who-has',
        psrc=src,
        pdst=next_hop,
    )
    ans = srp1(
        packet,
        iface=dev,
        timeout=timeout,
        verbose=False,
    )
    return ans


def get_hwsrc(ans) -> str:
    if not ans or not ans.haslayer(ARP):
        raise RuntimeError('failed to resolve MAC address from ARP response')
    return ans.getlayer(ARP).hwsrc

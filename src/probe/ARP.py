from scapy.all import (
    ARP,
    Ether,
    srp1,
)

from route.Route import get_route
from error import MwanProbeError


def get_next_hop(l3_src: str, l3_dst: str, dev: str) -> str:
    route = get_route(l3_dst, ['from', l3_src, 'oif', dev])
    return route.gateway or l3_dst


def arp_request(l3_src: str, l3_dst: str, dev: str, timeout: int):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(
        op='who-has',
        psrc=l3_src,
        pdst=l3_dst,
    )
    ans = srp1(
        packet,
        iface=dev,
        timeout=timeout,
        verbose=False,
    )
    return ans


def get_hwsrc(ans, dev: str, next_hop: str) -> str:
    if ans is None or not ans.haslayer(ARP):
        raise MwanProbeError(f'{dev} arp resolve {next_hop} failed')
    return ans.getlayer(ARP).hwsrc


def resolve_hwaddr(l3_src: str, l3_dst: str, dev: str, timeout: int) -> str:
    next_hop = get_next_hop(l3_src, l3_dst, dev)
    ans = arp_request(l3_src, next_hop, dev, timeout)
    return get_hwsrc(ans, dev, next_hop)


__all__ = ['resolve_hwaddr']

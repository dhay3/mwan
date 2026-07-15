from typing import NamedTuple

from scapy.all import ARP, Ether, get_if_addr, get_if_hwaddr, srp1
from route.Route import get_route


class LinkTarget(NamedTuple):
    dev: str
    src_addr: str
    src_mac: str
    dst_addr: str
    dst_mac: str


def get_next_hop(dev: str, src_addr: str, dst_addr: str) -> str:
    route = get_route(dst_addr, ['from', src_addr, 'oif', dev])
    return route.gateway or dst_addr


def resolve_mac(dev: str, src_addr: str, next_hop: str, timeout: int) -> str:
    request = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(
        op='who-has',
        psrc=src_addr,
        pdst=next_hop,
    )
    answer = srp1(
        request,
        iface=dev,
        timeout=timeout,
        verbose=False,
    )
    if not answer or not answer.haslayer(ARP):
        raise RuntimeError(f'failed to resolve {next_hop} on {dev}')

    return answer.getlayer(ARP).hwsrc


def resolve_target(dev: str, dst_addr: str, timeout: int) -> LinkTarget:
    src_addr = get_if_addr(dev)
    src_mac = get_if_hwaddr(dev)
    next_hop = get_next_hop(dev, src_addr, dst_addr)
    dst_mac = resolve_mac(dev, src_addr, next_hop, timeout)

    return LinkTarget(
        dev=dev,
        src_addr=src_addr,
        src_mac=src_mac,
        dst_addr=dst_addr,
        dst_mac=dst_mac,
    )


def ether(target: LinkTarget) -> Ether:
    return Ether(src=target.src_mac, dst=target.dst_mac)

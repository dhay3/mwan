from scapy.all import (
    Ether,
    ARP,
    srp1,
)


def arp_request(src: str, dst: str, dev: str, timeout: int):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(
        op='who-has',
        psrc=src,
        pdst=dst,
    )
    ans = srp1(
        packet,
        iface=dev,
        timeout=timeout,
        verbose=False,
    )
    return ans


def get_hwsrc(ans):
    if not ans or not ans.haslayer(ARP):
        pass
    return ans.getlayer(ARP).hwsrc

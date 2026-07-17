import logging
import uuid

from config import MwanConfig
from . import ICMP, TCP


logger = logging.getLogger('Probe')


def ping(config: MwanConfig, addr: str) -> bool:
    if ':' in addr:
        return TCP.ping(config, addr)
    return ICMP.ping(config, addr)


def probe(config: MwanConfig, enable_log: bool = True) -> bool:
    pulses = []
    uid = uuid.uuid4().hex[:4]
    for addr in config.probe.address:
        try:
            puls = ping(config, addr)
        except Exception as exc:
            puls = False
            if enable_log:
                logger.warning(
                    'trans:%s addr:%s probe error: %s',
                    uid,
                    addr,
                    exc,
                )
        if enable_log:
            if puls:
                logger.debug(f'trans:{uid} addr:{addr} succeeded')
            else:
                logger.debug(f'trans:{uid} addr:{addr} timeouted')
        pulses.append(puls)

    down = not any(pulses)
    return down


__all__ = [probe]

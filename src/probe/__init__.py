import logging
import uuid

from config import MwanConfig
from . import ICMP, TCP


logger = logging.getLogger("Probe")


def ping(config: MwanConfig, addr: str) -> bool:
    if ":" in addr:
        return TCP.ping(config, addr)
    return ICMP.ping(config, addr)


def probe(config: MwanConfig) -> bool:
    pulses = []
    uid = uuid.uuid4()
    for addr in config.probe.address:
        try:
            puls = ping(config, addr)
        except Exception as exc:
            raise RuntimeError(f"event_id:{uid}") from exc
        if not puls:
            logger.warning(f"event_id:{uid} addr:{addr} timeouted")
        pulses.append(puls)

    down = not any(pulses)
    return down


__all__ = [probe]

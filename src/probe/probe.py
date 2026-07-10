import logging
import uuid

from config.Config import MwanConfig
from probe import ICMP, TCP


logger = logging.getLogger("Probe")


def ping(config: MwanConfig, addr: str) -> bool:
    if ":" in addr:
        return TCP.ping(config, addr)
    return ICMP.ping(config, addr)


def ping_cycle(config: MwanConfig) -> bool:
    results = []
    uid = uuid.uuid4()
    for addr in config.probe.hosts:
        try:
            result = ping(config, addr)
        except Exception as exc:
            raise RuntimeError(f"event_id={uid}") from exc
        results.append(result)
    fail = not any(results)
    return fail

import logging
import uuid
from threading import Event

from config import MwanConfig
from config.State import STATE
from error import MwanProbeError
from . import ICMP, TCP


logger = logging.getLogger('Probe')


def ping(config: MwanConfig, addr: str) -> bool:
    if ':' in addr:
        return TCP.ping(config, addr)
    return ICMP.ping(config, addr)


def probe(
    config: MwanConfig,
    state: STATE,
    enable_log: bool = True,
    quit_event: Event | None = None,
) -> bool | None:
    pulses = []
    uid = uuid.uuid4().hex[:4]
    for addr in config.probe.address:
        if quit_event is not None and quit_event.is_set():
            return None

        try:
            puls = ping(config, addr)
        except MwanProbeError as exc:
            if enable_log:
                logger.debug(
                    'trans:%s addr:%s probe error: %s',
                    uid,
                    addr,
                    exc,
                )

        if quit_event is not None and quit_event.is_set():
            return None

        if enable_log:
            if puls:
                logger.debug(f'trans:{uid} addr:{addr} succeeded')
            else:
                logger.debug(f'trans:{uid} addr:{addr} timeouted')
        pulses.append(puls)

    if state == STATE.PRIMARY:
        if config.probe.down_strategy == 0:
            return any(pulses)
        return all(pulses)

    if state == STATE.BACKUP:
        if config.probe.up_strategy == 0:
            return all(pulses)
        return any(pulses)

    raise ValueError(f'unsupported probe state: {state}')


__all__ = [probe]

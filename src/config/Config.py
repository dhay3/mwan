from ipaddress import IPv4Address
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictStr,
    StrictInt,
    Field,
    model_validator,
)

from error import MwanConfigError

BoolInt = Annotated[StrictInt, Field(ge=0, le=1)]
PositiveInt = Annotated[StrictInt, Field(gt=0)]
NonEmptyStr = Annotated[StrictStr, Field(min_length=1)]


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        str_to_lower=True,
        extra='forbid',
    )


class GeneralConfig(BaseConfig):
    debug: BoolInt = Field(
        description='Enable debug log',
        default=0,
    )
    hot_reload: BoolInt = Field(
        description='Enable config hot-reload',
        default=1,
    )
    restore: BoolInt = Field(
        description='Enable routes restore',
        default=1,
    )


class PrimaryConfig(BaseConfig):
    dev: NonEmptyStr = Field(
        ...,
        description='Primary NIC',
        frozen=True,
    )
    step: PositiveInt = Field(
        description='Metric step',
        default=1,
    )


class BackupConfig(BaseConfig):
    dev: NonEmptyStr = Field(
        ...,
        description='Backup NIC',
        frozen=True,
    )


class ProbeConfig(BaseConfig):
    address: list[NonEmptyStr] = Field(
        description='Addresses for pings',
        default=[
            'dns.aliyun.com:80',
            '119.29.29.29',
        ],
        min_length=1,
        validate_default=True,
    )
    dns: list[IPv4Address] = Field(
        description='DNS servers',
        default=[
            IPv4Address('223.5.5.5'),
            IPv4Address('119.29.29.29'),
            IPv4Address('1.1.1.1'),
        ],
        min_length=1,
        validate_default=True,
    )

    count: PositiveInt = Field(
        description='Number of pings',
        default=1,
    )
    timeout: PositiveInt = Field(
        description='Seconds of ping timeout',
        default=1,
    )
    delay: PositiveInt = Field(
        description='Delay seconds between probes',
        default=3,
    )
    down: PositiveInt = Field(
        description='Number of DOWN probes to switch to backup',
        default=3,
    )
    down_strategy: BoolInt = Field(
        description='Strategy of probes mark DOWN (0: Passive 1: Positive)',
        default=1,
    )
    fast_failover: BoolInt = Field(
        description='Failover to backup route quickly on DOWN',
        default=0,
    )
    up: PositiveInt = Field(
        description='Number of UP Probes to switch back to primary',
        default=5,
    )
    up_strategy: BoolInt = Field(
        description='Strategy of probes mark UP (0: Passive 1: Positive)',
        default=0,
    )
    fast_recover: BoolInt = Field(
        description='Recover to primary route quickly on UP',
        default=0,
    )


class MwanConfig(BaseConfig):
    general: GeneralConfig = Field(alias='General')
    primary: PrimaryConfig = Field(alias='Primary')
    backup: BackupConfig = Field(alias='Backup')
    probe: ProbeConfig = Field(alias='Probe')

    @model_validator(mode='after')
    def validate(self):
        if self.primary.dev == self.backup.dev:
            raise MwanConfigError('NIC must be different')
        if self.probe.address:
            for addr in self.probe.address:
                if ':' not in addr:
                    continue
                if addr.count(':') != 1:
                    raise MwanConfigError(f'address invalid: {addr}')
                host, port = addr.split(':')
                if not host:
                    raise MwanConfigError(f'host missing: {addr}')
                if not port:
                    raise MwanConfigError(f'port missing: {addr}')
                if not port.isdecimal():
                    raise MwanConfigError(f'port non-numeric: {addr}')
                port = int(port)
                if port < 1 or port > 65535:
                    raise MwanConfigError(f'port out of range: {addr}')

        return self

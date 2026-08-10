from ipaddress import IPv4Address
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictStr,
    StrictInt,
    Field,
    model_validator,
)

from error import MwanConfigError


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        str_to_lower=True,
        extra='forbid',
    )


class GeneralConfig(BaseConfig):
    debug: Literal[0, 1] = Field(
        description='Enable debug log',
        default=0,
    )
    hot_reload: Literal[0, 1] = Field(
        description='Enable config hot reload',
        default=1,
    )
    restore: Literal[0, 1] = Field(
        description='Enable routes restore on exit',
        default=1,
    )


class PrimaryConfig(BaseConfig):
    dev: Annotated[StrictStr, Field(min_length=1)] = Field(
        ...,
        description='Primary NIC',
        frozen=True,
    )
    step: int = 1


class BackupConfig(BaseConfig):
    dev: Annotated[StrictStr, Field(min_length=1)] = Field(
        ...,
        description='Backup NIC',
        frozen=True,
    )


class ProbeConfig(BaseConfig):
    address: list[Annotated[StrictStr, Field(min_length=1)]] = Field(
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

    count: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Number of pings',
        default=1,
    )
    timeout: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Seconds of ping timeout',
        default=1,
    )
    delay: Annotated[StrictInt, Field(ge=3)] = Field(
        description='Delay seconds between probes',
        default=3,
    )
    down: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Number of DOWN probes to switch to backup',
        default=3,
    )
    down_strategy: Literal[0, 1] = Field(
        description='Strategy of probes mark DOWN (0: Passive 1: Positive)',
        default=1,
    )
    fast_failover: Literal[0, 1] = Field(
        description='Failover to backup route quickly on DOWN',
        default=0,
    )
    up: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Number of UP Probes to switch back to primary',
        default=5,
    )
    up_strategy: Literal[0, 1] = Field(
        description='Strategy of probes mark UP (0: Passive 1: Positive)',
        default=0,
    )
    fast_recover: Literal[0, 1] = Field(
        description='Recover to primary route quickly on UP',
        default=0,
    )


class MwanConfig(BaseConfig):
    general: GeneralConfig = Field(alias='General')
    primary: PrimaryConfig = Field(alias='Primary')
    backup: BackupConfig = Field(alias='Backup')
    probe: ProbeConfig = Field(alias='Probe')

    @model_validator(mode='after')
    def validate_nic(self):
        if self.primary.dev == self.backup.dev:
            raise MwanConfigError('NIC must be different')
        return self

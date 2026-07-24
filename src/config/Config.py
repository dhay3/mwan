from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictStr,
    StrictInt,
    Field,
)


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, str_to_lower=True)


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
        description='Addresses for ping',
        default=['dns.aliyun.com:80', '119.29.29.29'],
        validate_default=True,
    )

    count: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Number of ping',
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
        description='Number of DOWN probes to switch to Backup',
        default=3,
    )
    fast_down: Literal[0, 1] = Field(
        description='Failover quickly on DOWN',
        default=0,
    )
    up: Annotated[StrictInt, Field(ge=1)] = Field(
        description='Number of UP Probes to switch back to Primary',
        default=5,
    )
    fast_up: Literal[0, 1] = Field(
        description='Recover quickly on UP',
        default=0,
    )


class MwanConfig(BaseConfig):
    debug: Literal[0, 1] = Field(
        description='Enable debug log',
        default=0,
    )
    primary: PrimaryConfig = Field(alias='Primary')
    backup: BackupConfig = Field(alias='Backup')
    probe: ProbeConfig = Field(alias='Probe')

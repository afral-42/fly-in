from pydantic import BaseModel, model_validator, Field
from enum import Enum
from typing import Annotated, Self


class ZoneType(Enum):
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class Color(Enum):
    GRAY  = "gray"
    BLUE  = "blue"
    RED   = "red"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"


class ZoneMetadatas(BaseModel):
    zone: ZoneType = ZoneType.NORMAL
    color: Color = Color.GRAY
    max_drones: Annotated[int, Field(gt=0)] = 1


class ConnectionMetadatas(BaseModel):
    max_link_capacity: Annotated[int, Field(gt=0)] = 1


class Zone(BaseModel):
    name: Annotated[str, Field(pattern=r"^[^-]+$")]
    x: int
    y: int
    metadatas: ZoneMetadatas


class Connection(BaseModel):
    start_name: str
    end_name: str
    metadatas: ConnectionMetadatas

    @model_validator(mode='after')
    def validate_model(self) -> Self:
        if self.end_name == self.start_name:
            raise ValueError("End hub musts be different than start hub")
        return self


class FlyinConfig(BaseModel):
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    hubs: list[Zone]
    connections: list[Connection]

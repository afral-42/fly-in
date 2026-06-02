from pydantic import BaseModel, model_validator, Field, ConfigDict
from enum import Enum
from typing import Annotated, Any, Self


class ZoneType(Enum):
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class ZoneMetadatas(BaseModel):
    zone: ZoneType = ZoneType.NORMAL
    color: str = "white"
    max_drones: Annotated[int, Field(gt=0)] = 1

    model_config = ConfigDict(extra='forbid')


class ConnectionMetadatas(BaseModel):
    max_link_capacity: Annotated[int, Field(gt=0)] = 1

    model_config = ConfigDict(extra='forbid')


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
    nb_drones: Annotated[int, Field(gt=0)]
    start_hub: Zone
    end_hub: Zone
    hubs: list[Zone]
    connections: list[Connection]

    @model_validator(mode='before')
    @classmethod
    def inject_default_capacity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            nb_drones = data.get('nb_drones')
            if nb_drones is not None:
                for hub_key in ('start_hub', 'end_hub'):
                    hub = data.get(hub_key)
                    if isinstance(hub, dict):
                        metadatas = hub.get('metadatas')
                        if metadatas is None:
                            metadatas = {}
                            hub['metadatas'] = metadatas

                        if isinstance(metadatas, dict) and 'max_drones' not in metadatas:
                            metadatas['max_drones'] = nb_drones
        return data

    @model_validator(mode='after')
    def validate_unique_connections(self) -> Self:
        seen_connections = set()
        
        for conn in self.connections:
            normalized_conn = tuple(sorted([conn.start_name, conn.end_name]))
            
            if normalized_conn in seen_connections:
                raise ValueError(
                    f"Duplicate connection detected: {conn.start_name}-{conn.end_name}"
                )
            
            seen_connections.add(normalized_conn)
            
        return self

    @model_validator(mode='after')
    def validate_model(self) -> Self:
        if (
            self.start_hub.metadatas.max_drones < self.nb_drones or
            self.end_hub.metadatas.max_drones < self.nb_drones
        ):
            raise ValueError(
                f"Start hub and end hub can't have less than {self.nb_drones} drones"
            )
        return self

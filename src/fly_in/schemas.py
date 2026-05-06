from pydantic import BaseModel


class Zone(BaseModel):
    name: str
    x: int
    y: int


class Connection(BaseModel):
    start_name: str
    end_name: str


class FlyinConfig(BaseModel):
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    hubs: list[Zone]
    connections: list[Connection]

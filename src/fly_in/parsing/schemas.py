from enum import Enum
from typing import Annotated, Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ZoneType(Enum):
    """Enumeration of possible zone types for hubs and areas."""

    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class ZoneMetadatas(BaseModel):
    """Metadata for a zone/hub describing color, capacity and type.

    Attributes:
        zone: The `ZoneType` for the hub (normal, restricted, etc.).
        color: The display color name for rendering.
        max_drones: Maximum number of drones that can be present.
    """

    zone: ZoneType = ZoneType.NORMAL
    color: str = "white"
    max_drones: Annotated[int, Field(gt=0)] = 1

    model_config = ConfigDict(extra="forbid")


class ConnectionMetadatas(BaseModel):
    """Metadata for a connection such as its maximum capacity."""

    max_link_capacity: Annotated[int, Field(gt=0)] = 1

    model_config = ConfigDict(extra="forbid")


class Zone(BaseModel):
    """Schema representing a hub/zone in the configuration.

    Fields:
        name: Hub name (must not contain '-').
        x: X coordinate (int).
        y: Y coordinate (int).
        metadatas: Additional `ZoneMetadatas` for the hub.
    """

    name: Annotated[str, Field(pattern=r"^[^-]+$")]
    x: int
    y: int
    metadatas: ZoneMetadatas


class Connection(BaseModel):
    """Schema representing a connection between two named hubs.

    Validates that `start_name` and `end_name` are not identical.
    """

    start_name: str
    end_name: str
    metadatas: ConnectionMetadatas

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        """Ensure that a connection does not join a hub to itself.

        Returns:
            The instance `Self` if validation passes.
        Raises:
            ValueError: If `start_name` and `end_name` are equal.
        """
        if self.end_name == self.start_name:
            raise ValueError("End hub musts be different than start hub")
        return self


class FlyinConfig(BaseModel):
    """Top-level configuration schema for the Fly-in simulation.

    This model contains the drone count, start/end hubs, intermediary
    hubs, and bidirectional connections between hubs. It also
    performs validators to inject defaults and ensure consistency.
    """

    nb_drones: Annotated[int, Field(gt=0, lt=200)]
    start_hub: Zone
    end_hub: Zone
    hubs: list[Zone]
    connections: list[Connection]

    @model_validator(mode="before")
    @classmethod
    def inject_default_capacity(cls, data: Any) -> Any:
        """Inject default `max_drones` into start/end hubs if missing.

        When the input `data` is a dict and `nb_drones` is present,
        this validator sets `max_drones` on start and end hubs to the
        drone count if not explicitly provided.
        """
        if isinstance(data, dict):
            nb_drones = data.get("nb_drones")
            if nb_drones is not None:
                for hub_key in ("start_hub", "end_hub"):
                    hub = data.get(hub_key)
                    if isinstance(hub, dict):
                        metadatas = hub.get("metadatas")
                        if metadatas is None:
                            metadatas = {}
                            hub["metadatas"] = metadatas

                        if (
                            isinstance(metadatas, dict)
                            and "max_drones" not in metadatas
                        ):
                            metadatas["max_drones"] = nb_drones
        return data

    @model_validator(mode="after")
    def validate_unique_connections(self) -> Self:
        """Ensure there are no duplicate undirected connections.

        Treats connections as undirected by normalizing names and
        raises `ValueError` if a duplicate is detected.
        """
        seen_connections = set()

        for conn in self.connections:
            normalized_conn = tuple(sorted([conn.start_name, conn.end_name]))

            if normalized_conn in seen_connections:
                raise ValueError(
                    "Duplicate connection detected: "
                    f"{conn.start_name}-{conn.end_name}"
                )

            seen_connections.add(normalized_conn)

        return self

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        """Validate start/end hub capacities against `nb_drones`.

        Ensures that both the start and end hubs can accommodate the
        total number of drones; raises `ValueError` otherwise.
        """
        if (
            self.start_hub.metadatas.max_drones < self.nb_drones
            or self.end_hub.metadatas.max_drones < self.nb_drones
        ):
            raise ValueError(
                "Start hub and end hub can't have less than "
                f"{self.nb_drones} drones"
            )
        return self

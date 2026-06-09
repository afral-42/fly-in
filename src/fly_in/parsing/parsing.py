import re
from collections.abc import Iterator
from enum import Enum
from typing import Any, cast

from fly_in.parsing.schemas import FlyinConfig


class ParsingError(Exception):
    """Exception raised for parsing-related errors.

    Attributes:
        details: A human-readable message describing the error.
        line: Optional line number where the error occurred.
    """
    def __init__(self, details: str, line: int | None = None) -> None:
        prefix = (
            f"Parsing error on line {line}:\n"
            if line is not None
            else "Parsing error:\n"
        )
        super().__init__(f"{prefix}{details}")


class ConfigKey(Enum):
    """Enumeration of valid configuration keys in the map files."""
    NB_DRONES = "nb_drones"
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    CONNECTION = "connection"


class ConfigParser:
    """Parser for Fly-in configuration files.

    This class reads a configuration file, validates its syntax and
    converts it into a structure suitable for `FlyinConfig` creation.
    """
    EXTRACT_METADATAS = re.compile(r"\[([^\[\]]*)\]")
    METADATA_POSITION = re.compile(r"\[[^\[\]]*\]")

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.hub_names: set[str] = set()
        self.hub_coordinates: set[tuple[str, str]] = set()

    def _parse_config_file(self) -> Iterator[tuple[ConfigKey, str, int]]:
        """Yield raw parsed lines as (key, value, line).

        Reads the configuration file and yields tuples containing the
        parsed `ConfigKey`, the raw value string (including any
        metadata), and the 1-based line number.
        """
        try:
            with open(self.config_path, "r") as f:
                for line, content in enumerate(f, start=1):
                    if not content.strip():
                        continue
                    try:
                        content = content.split("#", 1)[0]
                        if not content.strip():
                            continue
                        key_str, value = content.split(":")
                    except ValueError:
                        raise ParsingError(
                            "Invalid config file format, "
                            "please use key: value syntax",
                            line,
                        )
                    try:
                        key = ConfigKey(key_str)
                    except ValueError:
                        raise ParsingError(
                            f"Invalid config key {key_str}", line
                        )

                    yield (key, value, line)

        except PermissionError:
            raise ParsingError("Permission error opening config file")
        except FileNotFoundError:
            raise ParsingError(
                "File not found error: cannot locate config file"
            )

    def _extract_metadatas(self, key: ConfigKey, value: str, line: int) -> str:
        """Extract metadata bracket contents from a config value.

        Args:
            key: The `ConfigKey` for context when raising errors.
            value: The raw value string possibly containing metadatas.
            line: Line number for error reporting.

        Returns:
            The metadata string found inside square brackets, or empty
            string if none present.
        """
        metadatas = self.EXTRACT_METADATAS.findall(value)
        if len(metadatas) == 1:
            metadata = metadatas[0]
        elif len(metadatas) == 0:
            metadata = ""
        else:
            raise ParsingError(
                f"Invalid {key.value} config file format,"
                f"please use only one metadata group",
                line,
            )

        return cast(str, metadata)

    def _extract_params(self, value: str) -> str:
        """Return the parameter portion of a value without metadata.

        Strips the metadata bracket expression from the provided value
        string and returns the remaining parameters part.
        """
        return self.METADATA_POSITION.sub("", value)

    def _parse_metadatas(
        self, raw_metadatas: str, line: int
    ) -> dict[str, str]:
        """Parse a metadata key=value string into a dictionary.

        Args:
            raw_metadatas: The raw metadata string (space separated
                `key=value` pairs).
            line: Line number for error reporting.

        Returns:
            A dict mapping metadata keys to values.
        """
        metadatas = {}

        for metadata in raw_metadatas.split():
            try:
                key, value = metadata.split("=")
                if not key or not value:
                    raise ValueError
            except ValueError:
                raise ParsingError(
                    "Invalid config file format, "
                    "please use 'key=value' for metadatas",
                    line,
                )

            metadatas[key] = value

        return metadatas

    def _parse_connection(
        self, params: str, metadatas: str, line: int
    ) -> dict[str, str | dict[str, str]]:
        """Parse a connection line into its components.

        Validates that referenced hub names exist and returns a
        dictionary suitable for constructing a `Connection` schema.
        """
        try:
            path = params
            start, end = path.split("-")
        except ValueError:
            raise ParsingError(
                "Invalid connection config file format, "
                "please use 'start_name - end_name'",
                line,
            )

        if start.strip() not in self.hub_names:
            raise ParsingError(
                f"Invalid connection '{start.strip()}',"
                f" it musts be a valid hub {self.hub_names}"
            )
        if end.strip() not in self.hub_names:
            raise ParsingError(
                f"Invalid connection '{end.strip()}',"
                f" it musts be a valid hub {self.hub_names}"
            )

        return {
            "start_name": start.strip(),
            "end_name": end.strip(),
            "metadatas": self._parse_metadatas(metadatas, line),
        }

    def _parse_zone(
        self, params: str, metadatas: str, key: ConfigKey, line: int
    ) -> dict[str, str | dict[str, str]]:
        """Parse a hub/start/end zone line into its components.

        Ensures hub names and coordinates are unique and returns a
        dictionary suitable for constructing a `Zone` schema.
        """
        try:
            name, x, y = params.split()
        except ValueError:
            raise ParsingError(
                f"Invalid {key.value} config file format, "
                f"please use '{key.value}: name x y [metadatas]' syntax",
                line,
            )

        if name in self.hub_names or (x, y) in self.hub_coordinates:
            raise ParsingError(
                "Hubs can't have similar names or "
                f"coordinates ({name}, {x}, {y})",
                line,
            )

        self.hub_coordinates.add((x, y))
        self.hub_names.add(name)

        result: dict[str, str | dict[str, str]] = {
            "name": name.strip(),
            "x": x.strip(),
            "y": y.strip(),
            "metadatas": self._parse_metadatas(metadatas, line),
        }
        return result

    def parse(self) -> FlyinConfig:
        """Parse the configuration file and return a `FlyinConfig`.

        Reads the file, parses hubs, connections and metadata, and
        validates the overall structure. Raises `ParsingError` on any
        syntax or semantic issues.
        """
        connections: list[dict[str, str | dict[str, str]]] = []
        hubs: list[dict[str, str | dict[str, str]]] = []

        config: dict[str, list[dict[Any, Any]] | dict[Any, Any] | str] = {
            "hubs": hubs,
            "connections": connections,
        }

        first_line = True

        for key, value, line in self._parse_config_file():
            if key == ConfigKey.NB_DRONES:
                if not first_line:
                    raise ParsingError(
                        "nb_drones must be specified on first line"
                    )
                config[key.value] = value.strip()

            elif key in [
                ConfigKey.START_HUB,
                ConfigKey.END_HUB,
                ConfigKey.HUB,
                ConfigKey.CONNECTION,
            ]:
                metadatas = self._extract_metadatas(key, value, line)
                params = self._extract_params(value)

                if key == ConfigKey.CONNECTION:
                    connections.append(
                        self._parse_connection(params, metadatas, line)
                    )

                else:
                    result = self._parse_zone(params, metadatas, key, line)
                    if key in [ConfigKey.START_HUB, ConfigKey.END_HUB]:
                        if key.value in config:
                            raise ParsingError(
                                f"Config must have a unique {key.value}"
                            )
                        config[key.value] = result
                    elif key == ConfigKey.HUB:
                        hubs.append(result)

            if first_line:
                first_line = False

        try:
            return FlyinConfig.model_validate(config)
        except ValueError as e:
            raise ParsingError(str(e))

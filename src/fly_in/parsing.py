from enum import Enum
import re
from typing import Callable

from fly_in.schemas import FlyinConfig, Zone


class ParsingError(Exception):
    def __init__(self, details: str, line: int | None = None) -> None:
        prefix = (f"Parsing error on line {line}:\n"
            if line is not None else "Parsing error:\n"
        )
        super().__init__(f"{prefix}{details}")


class ConfigKey(Enum):
    NB_DRONES = "nb_drones"
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    CONNECTION = "connection"


class ConfigParser:
    EXTRACT_METADATAS = re.compile(r"\[([^\[\]]*)\]")
    METADATA_POSITION = re.compile(r"\[[^\[\]]*\]")

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.hub_names: set[str] = set()
        self.hub_coordinates: set[tuple[str, str]] = set()

    def _parse_config_file(self):
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
                            "please use key: value syntax", line
                        )
                    try:
                        key = ConfigKey(key_str)
                    except ValueError:
                        raise ParsingError(f"Invalid config key {key_str}", line)

                    yield (key, value, line)

        except PermissionError:
            raise ParsingError("Permission error opening config file")
        except FileNotFoundError:
            raise ParsingError("File not found error: cannot locate config file")


    def _extract_metadatas(self, key: ConfigKey, value: str, line: int) -> str:
        metadatas = self.EXTRACT_METADATAS.findall(value)
        if len(metadatas) == 1:
            metadata = metadatas[0]
        elif len(metadatas) == 0:
            metadata = ""
        else:
            raise ParsingError(
                f"Invalid {key.value} config file format,"
                f"please use only one metadata group", line
            )

        return metadata


    def _extract_params(self, value: str) -> str:
        params = self.METADATA_POSITION.sub("", value)
        return params

    def _parse_metadatas(self, raw_metadatas: str, line: int) -> dict[str, str]:
        metadatas = {}

        for metadata in raw_metadatas.split():
            try:
                key, value = metadata.split("=")
                if not key or not value:
                    raise ValueError
            except ValueError:
                raise ParsingError(
                    f"Invalid config file format, "
                    f"please use 'key=value' for metadatas", line
                )

            metadatas[key] = value

        return metadatas

    def _parse_connection(
        self,
        params: str,
        metadatas: str,
        line: int
    ) -> dict[str, str | dict[str, str]]:
        try:
            path = params
            start, end = path.split("-")
        except ValueError:
            raise ParsingError(
                "Invalid connection config file format, "
                "please use 'start_name - end_name'", line
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
            "metadatas": self._parse_metadatas(metadatas, line)
        }

    def _parse_zone(
        self,
        params: str,
        metadatas: str,
        key: ConfigKey,
        line
    ) -> dict[str, str | dict[str, str]]:
        try:
            name, x, y = params.split()
        except ValueError:
            raise ParsingError(
                f"Invalid {key.value} config file format, "
                f"please use '{key.value}: name x y [metadatas]' syntax", line
            )

        if name in self.hub_names or (x, y) in self.hub_coordinates:
            raise ParsingError(
                "Hubs can't have similar names or "
                f"coordinates ({name}, {x}, {y})", line
            )
    
        self.hub_coordinates.add((x, y))
        self.hub_names.add(name)

        result: dict[str, str | dict[str, str]] = {
            "name": name.strip(),
            "x": x.strip(),
            "y": y.strip(),
            "metadatas": self._parse_metadatas(metadatas, line)
        }
        return result

    def parse(self) -> FlyinConfig:
        connections: list[dict[str, str | dict[str, str]]] = []
        hubs: list[dict[str, str | dict[str, str]]] = []

        config: dict[str, list[dict] | dict | str] = {
            "hubs": hubs,
            "connections": connections
        }

        first_line = True

        for key, value, line in self._parse_config_file():
            if key == ConfigKey.NB_DRONES:
                if not first_line:
                    raise ParsingError("nb_drones must be specified on first line")
                config[key.value] = value.strip()

            elif key in [ConfigKey.START_HUB, ConfigKey.END_HUB, ConfigKey.HUB, ConfigKey.CONNECTION]:
                metadatas = self._extract_metadatas(key, value, line)
                params = self._extract_params(value)

                if key == ConfigKey.CONNECTION:
                    connections.append(self._parse_connection(params, metadatas, line))

                else:
                    result = self._parse_zone(params, metadatas, key, line)
                    if key in [ConfigKey.START_HUB, ConfigKey.END_HUB]:
                        if key.value in config:
                            raise ParsingError(f"Config must have a unique {key.value}")
                        config[key.value] = result
                    elif key == ConfigKey.HUB:
                        hubs.append(result)

            if first_line:
                first_line = False

        try:
            return FlyinConfig.model_validate(config)
        except ValueError as e:
            raise ParsingError(str(e))


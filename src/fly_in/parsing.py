from enum import Enum
import re

from fly_in.schemas import FlyinConfig, Zone


class ParsingError(Exception):
    def __init__(self, details: str) -> None:
        super().__init__(f"Parsing error: {details}")


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

    def _parse_config_file(self):
        try:
            with open(self.config_path, "r") as f:
                while content := f.readline():
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
                            "please use key: value syntax"
                        )
                    try:
                        key = ConfigKey(key_str)
                    except ValueError:
                        raise ParsingError(f"Invalid config key {key_str}")

                    yield (key, value)

        except PermissionError:
            raise ParsingError("Permission error opening config file")
        except FileNotFoundError:
            raise ParsingError("File not found error: cannot locate config file")
        except Exception as e:
            raise ParsingError(f"Unexpected error reading config file {e}")


    def _extract_metadatas(self, key: ConfigKey, value: str) -> str | None:
        metadatas = self.EXTRACT_METADATAS.findall(value)
        if len(metadatas) == 1:
            metadata = metadatas[0]
        elif len(metadatas) == 0:
            metadata = ""
        else:
            raise ParsingError(
                f"Invalid {key.value} config file format:"
                f" please use only one metadata group"
            )

        return metadata


    def _extract_params(self, value: str) -> str:
        params = self.METADATA_POSITION.sub("", value)
        return params

    def _parse_metadatas(self, raw_metadatas: str) -> dict[str, str]:
        metadatas = {}

        for metadata in raw_metadatas.split():
            try:
                key, value = metadata.split("=")
            except ValueError:
                raise ParsingError(
                    f"Invalid config file format:"
                    f" please use key=value for metadatas"
                )

            metadatas[key] = value

        return metadatas

    def _parse_connection(
        self,
        params: str,
        metadatas: str
    ) -> dict[str, str | dict[str, str]]:
        try:
            path = params
            start, end = path.split("-")
        except ValueError:
            raise ParsingError(
                "Invalid starthub config file format:"
                " please use start_hub: name x y"
                " please use key: value syntax"
            )

        return {
            "start_name": start.strip(),
            "end_name": end.strip(),
            "metadatas": self._parse_metadatas(metadatas)
        }
    
    def _parse_zone(self, params: str, metadatas: str, key: ConfigKey) -> dict[str, str | dict[str, str]]:
        try:
            name, x, y = params.split()
        except ValueError:
            raise ParsingError(
                f"Invalid {key.value} config file format:"
                f" please use {key.value}: name x y"
                " please use key: value syntax"
            )

        result: dict[str, str | dict[str, str]] = {
            "name": name.strip(),
            "x": x.strip(),
            "y": y.strip(),
            "metadatas": self._parse_metadatas(metadatas)
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

        for key, value in self._parse_config_file():
            if key == ConfigKey.NB_DRONES:
                if not first_line:
                    raise ParsingError("nb_drones must be specified on first line")
                config[key.value] = value.strip()

            elif key in [ConfigKey.START_HUB, ConfigKey.END_HUB, ConfigKey.HUB, ConfigKey.CONNECTION]:
                metadatas = self._extract_metadatas(key, value)
                params = self._extract_params(value)

                if key == ConfigKey.CONNECTION:
                    connections.append(self._parse_connection(params, metadatas))

                else:
                    result = self._parse_zone(params, metadatas, key)
                    if key in [ConfigKey.START_HUB, ConfigKey.END_HUB]:
                        if key.value in config:
                            raise ParsingError(f"Config must have a unique {key.value}")
                        config[key.value] = result
                    elif key == ConfigKey.HUB:
                        hubs.append(result)

            if first_line:
                first_line = False

        print(config)
        return FlyinConfig.model_validate(config)

import re

from fly_in.schemas import FlyinConfig, Zone


class ParsingError(Exception):
    def __init__(self, details: str) -> None:
        super().__init__(f"Parsing error: {details}")


class ConfigParser:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path

    def parse(self) -> FlyinConfig:
        connections: list[dict[str, str]] = []
        hubs: list[dict[str, str]] = []
        config: dict[str, list[dict] | dict | str] = {
            "hubs": hubs,
            "connections": connections
        }

        EXTRACT_METADATAS = r"\[([^\[\]]*)\]"
        METADATA_POSITION = r"\[[^\[\]]*\]"

        try:
            with open(self.config_path, "r") as f:
                while content := f.readline():
                    if not content.strip():
                        continue
                    try:
                        key, value = content.split(":")
                    except ValueError:
                        raise ParsingError(
                            "Invalid config file format, "
                            "please use key: value syntax"
                        )

                    if key == "nb_drones":
                        config["nb_drones"] = value.strip()

                    elif key in ["start_hub", "end_hub"]:
                        metadatas = re.findall(EXTRACT_METADATAS, value)
                        if len(metadatas) == 1:
                            metadata = metadatas[0]
                        elif len(metadatas) == 0:
                            metadata = None
                        else:
                            raise ParsingError(
                                f"Invalid {key} config file format:"
                                f" please use only one metadata group"
                            )
                        print(metadata)
                        params = re.sub(METADATA_POSITION, "", value)
                        try:
                            name, x, y = params.split()
                        except ValueError:

                            raise ParsingError(
                                f"Invalid {key} config file format:"
                                f" please use {key}: name x y"
                                " please use key: value syntax"
                            )
                        config[key] = {
                            "name": name.strip(),
                            "x": x.strip(),
                            "y": y.strip()
                        }

                    elif key == "hub":
                        metadatas = re.findall(EXTRACT_METADATAS, value)
                        if len(metadatas) == 1:
                            metadata = metadatas[0]
                        elif len(metadatas) == 0:
                            metadata = None
                        else:
                            raise ParsingError(
                                f"Invalid {key} config file format:"
                                f" please use only one metadata group"
                            )
                        print(metadata)
                        params = re.sub(METADATA_POSITION, "", value)
                        try:
                            name, x, y = params.split()
                        except ValueError:
                            raise ParsingError(
                                f"Invalid {key} config file format:"
                                f" please use {key}: name x y"
                                " please use key: value syntax"
                            )

                        hubs.append({
                            "name": name.strip(),
                            "x": x.strip(),
                            "y": y.strip()
                        })

                    elif key == "connection":
                        metadatas = re.findall(EXTRACT_METADATAS, value)
                        if len(metadatas) == 1:
                            metadata = metadatas[0]
                        elif len(metadatas) == 0:
                            metadata = None
                        else:
                            raise ParsingError(
                                f"Invalid {key} config file format:"
                                f" please use only one metadata group"
                            )
                        print(metadata)

                        params = re.sub(METADATA_POSITION, "", value)
                        try:
                            path = params
                            start, end = path.split("-")
                        except ValueError:
                            raise ParsingError(
                                "Invalid starthub config file format:"
                                " please use start_hub: name x y"
                                " please use key: value syntax"
                            )

                        connections.append({
                            "start_name": start.strip(),
                            "end_name": end.strip()
                        })

        except PermissionError:
            raise ParsingError("Permission error opening config file")
        except FileNotFoundError:
            raise ParsingError("Permission error opening config file")
        except Exception as e:
            raise ParsingError(f"Unexpected error reading config file {e}")
        
        print(config)
        return FlyinConfig.model_validate(config)

from fly_in.parsing import ConfigParser, ParsingError

def main() -> None:
    try:
        parser = ConfigParser("salut.txt")
        config = parser.parse()

        print(config.model_dump_json(indent=4))
    except ParsingError as e:
        print(e)


if __name__ == "__main__":
    main()

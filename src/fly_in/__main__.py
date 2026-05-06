from fly_in.parsing import ConfigParser

def main() -> None:
    parser = ConfigParser("salut.txt")
    parser.parse()


if __name__ == "__main__":
    main()

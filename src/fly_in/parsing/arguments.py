import sys
from pathlib import Path
import questionary


def get_map_path(folder_path: str = "maps") -> str:
    """Retrieves the map file path either via CLI argument / interactive menu.

    If a command-line argument is provided, it returns that argument directly
    (useful for peer evaluations). Otherwise, it displays an interactive menu
    using questionary to select a map from the specified folder.

    Args:
        folder_path (str): The path to the directory containing map files.
            Defaults to "maps".

    Returns:
        str: The string representation of the selected map file path.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]

    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        print(f"Error: Directory '{folder}' not found.", file=sys.stderr)
        sys.exit(1)

    map_files = [f.name for f in folder.glob("*") if f.is_file()]

    if not map_files:
        print(f"Error: No map files available in '{folder}'.", file=sys.stderr)
        sys.exit(1)

    selected_file = questionary.select(
        "Which map do you want to run?", choices=map_files
    ).ask()

    if not selected_file:
        sys.exit(0)

    return str(folder / selected_file)

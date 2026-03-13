import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE_INPUT_PATH = os.path.join(BASE_DIR, "res", "Txt", "DuLieu.txt")
FILE_OUTPUT_PATH = os.path.join(BASE_DIR, "res", "Txt", "KetQua.txt")


def read_file():
    """Read level options from the data file."""
    items = []
    try:
        with open(FILE_INPUT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                for s in line.strip().split():
                    if s:
                        items.append(s)
    except FileNotFoundError:
        print(f"File not found: {FILE_INPUT_PATH}")
    except IOError as e:
        print(f"Error reading file: {e}")
    if not items:
        items = ["3x3", "4x4", "5x5", "6x6"]
    return items


def write_file(time_str: str, count: str):
    """Append game result to the output file."""
    try:
        os.makedirs(os.path.dirname(FILE_OUTPUT_PATH), exist_ok=True)
        with open(FILE_OUTPUT_PATH, "a", encoding="utf-8") as f:
            f.write(f"{time_str}(s) - {count} Clicks\n")
    except IOError as e:
        print(f"Error writing file: {e}")

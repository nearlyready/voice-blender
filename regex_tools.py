import re
import shutil
from pathlib import Path

def copy(source_pattern, target_pattern, root="."):
    """
    Copy files matching a regex to new paths defined by a target pattern.

    Args:
        source_pattern (str): regex to match source file paths.
        target_pattern (str): target path pattern, can use \1, \2, ... from source_pattern.
        root (str or Path): directory to start searching from.
    """
    regex = re.compile(source_pattern)
    root = Path(root)

    for path in root.rglob("*"):  # recursively walk all files
        if path.is_file():
            match = regex.match(str(path))
            if match:
                # build target path using captured groups
                target_path = Path(match.expand(target_pattern))
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target_path)
                print(f"Copied {path} → {target_path}")

# Example usage:
# copy(r"data/raw/(.*)\.txt", r"data/processed/\1.csv")

if __name__ == "__main__":
    copy(r"tests/regex_copy/(.*?)/(.*)\.txt", r"tests/regex_copy/output/\2_\1.txt")

import re
import shutil
from pathlib import Path

def regex_copy(source_pattern, target_pattern, dry_run=True, root=".", verbose=False):
    """
    Copy files matching a regex to new paths defined by a target pattern.

    Args:
        source_pattern (str): regex to match source file paths.
        target_pattern (str): target path pattern, can use \1, \2, ... from source_pattern.
        dry_run (bool): if True, only print the actions that would be taken without actually copying files. Useful for preventing mistakes.
        root (str or Path): directory to start searching from, e.g. root=relative/path/to/root/folder. To save time, set the root to the folder that you are searching within.
        verbose (bool): if True, print detailed debug information. Useful if you don't understand why files are not copying.
    """
    regex = re.compile(source_pattern.replace('/', r'[/\\]'))
    root = Path(root)

    if dry_run:
        print(f"{'-'*20}\nWARNING: This is a dry run. No files will be copied. To copy files, set dry_run=False\n{'-'*20}")

    for path in root.rglob("*"):
        if path.is_file():
            # Convert path to string with forward slashes for consistent matching
            path_str = str(path).replace('\\', '/')
            if verbose:
                print(f"Testing path: {path_str}")
            
            match = regex.match(path_str)
            if match:
                # Build target path using captured groups
                target_path = Path(match.expand(target_pattern))
                if dry_run:
                    print(f"  - Would copy {path} → {target_path}")
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target_path)
                    print(f"  - Copied {path} → {target_path}")
            else:
                if verbose:
                    print(f"  - No match for {path_str}")


# Example usage:
# copy(r"data/raw/(.*)\.txt", r"data/processed/\1.csv")

if __name__ == "__main__":
    regex_copy(r"tests/regex_copy/(.*?)/(.*)\.txt", r"tests/regex_copy/output/\2_\1.txt")

from pathlib import Path
import os


def ensure_path_exists(path, create_if_missing=False, is_file=None) -> bool:
    """
    Ensure that a given path (file or directory) exists. Optionally creates it.

    Args:
        path (str | Path): The path to check (file or directory).
        create_if_missing (bool): If True, creates the path if it doesn't exist.
        is_file (bool | None): If True, path is treated as a file. If False, as a directory.
                               If None, inferred automatically.

    Returns:
        bool: True if path exists or was successfully created, False otherwise.
    """
    path = Path(path)

    if path.exists():
        return True

    if not create_if_missing:
        return False

    try:
        if is_file is None:
            is_file = bool(path.suffix)

        if is_file:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)

        return True
    except Exception as e:
        print(f"[ERROR] Failed to create path '{path}': {e}")
        return False

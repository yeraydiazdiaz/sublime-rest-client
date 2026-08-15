import os
from glob import glob
from typing import List, Optional, Sequence


def dotenv_paths(
    folders: Sequence[str], file_name: Optional[str] = None
) -> List[str]:
    """Existing `.env` and `*.env` paths, outermost first.

    Project folders are scanned first, then the request file's directory and its
    ancestors up to the project folder containing it, ending with the file's own
    directory. Callers load them in order, so the closest file wins.
    """
    dirs = [os.path.abspath(folder) for folder in folders]

    if file_name:
        ancestors = []
        current = os.path.dirname(os.path.abspath(file_name))
        while True:
            ancestors.append(current)
            parent = os.path.dirname(current)
            # ponytail: walk stops at a project folder, or at the filesystem
            # root for files opened outside any project
            if current in dirs or parent == current:
                break
            current = parent
        dirs += reversed(ancestors)

    paths: List[str] = []
    for directory in dirs:
        candidates = [os.path.join(directory, ".env")]
        candidates += sorted(glob(os.path.join(directory, "*.env")))
        for path in candidates:
            if os.path.isfile(path) and path not in paths:
                paths.append(path)

    return paths

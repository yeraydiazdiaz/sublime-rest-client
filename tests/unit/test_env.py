import sys
from pathlib import Path

sys.path.append("deps")

from dotenv import dotenv_values  # noqa: E402

from rest_client import env  # noqa: E402


def test_no_dotenv_files(tmp_path: Path) -> None:
    (tmp_path / "api.http").write_text("GET https://example.com")

    assert env.dotenv_paths([str(tmp_path)], str(tmp_path / "api.http")) == []


def test_dotenv_in_project_folder(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=root")

    assert env.dotenv_paths([str(tmp_path)]) == [str(tmp_path / ".env")]


def test_nested_dotenv_overrides_project_folder(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=root")
    http_dir = tmp_path / "http"
    http_dir.mkdir()
    (http_dir / ".env").write_text("TOKEN=local")

    paths = env.dotenv_paths([str(tmp_path)], str(http_dir / "api.http"))

    # closest last so callers loading in order let it win
    assert paths == [str(tmp_path / ".env"), str(http_dir / ".env")]


def test_walks_up_intermediate_directories(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    (tmp_path / "a" / ".env").write_text("TOKEN=middle")
    (deep / ".env").write_text("TOKEN=deep")

    paths = env.dotenv_paths([str(tmp_path)], str(deep / "api.http"))

    assert paths == [str(tmp_path / "a" / ".env"), str(deep / ".env")]


def test_named_env_files_after_dotenv(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=dot")
    (tmp_path / "staging.env").write_text("TOKEN=staging")

    assert env.dotenv_paths([str(tmp_path)]) == [
        str(tmp_path / ".env"),
        str(tmp_path / "staging.env"),
    ]


def test_vars_merge_per_name_closest_wins(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=root\nHOST=api.example.com")
    http_dir = tmp_path / "http"
    http_dir.mkdir()
    (http_dir / ".env").write_text("TOKEN=local")

    dotenv_vars = {}
    for path in env.dotenv_paths([str(tmp_path)], str(http_dir / "api.http")):
        dotenv_vars.update(dotenv_values(path))

    assert dotenv_vars == {"TOKEN": "local", "HOST": "api.example.com"}


def test_no_file_name_only_scans_project_folders(tmp_path: Path) -> None:
    http_dir = tmp_path / "http"
    http_dir.mkdir()
    (http_dir / ".env").write_text("TOKEN=local")

    assert env.dotenv_paths([str(tmp_path)]) == []

import re

from pathlib import Path


def safe_filename(
    value: str,
    fallback: str = "comic"
) -> str:

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    value = value.strip("_")

    if not value:

        return fallback

    return value[:80]


def public_static_path(
    path: Path,
    static_dir: Path
) -> str:

    relative = (
        path
        .resolve()
        .relative_to(
            static_dir.resolve()
        )
    )

    return (
        "/static/"
        + relative.as_posix()
    )
"""Tools to work with plugin resource files (icons, images), without a compiled QRC resource file."""

from pathlib import Path


def plugin_path(*args) -> Path:
    """Return the path to the plugin root folder."""
    path = Path(__file__).resolve().parent
    for item in args:
        path = path.joinpath(item)

    return path


def resources_path(*args) -> Path:
    """Return the path to the plugin images folder."""
    return plugin_path("images", *args)

from pathlib import Path

import typer
from typing_extensions import Annotated

from xif.config import Config
from xif.main import add_exif, get_exif, get_exif_from_image

app = typer.Typer()


def print_table(data: dict[str, str]) -> None:
    key_len = max(len(key) for key in data.keys())
    for key, value in data.items():
        print(f"{key + ':':.<{key_len}} {value}")


@app.command(help="Add EXIF data to an image")
def add(
    directory: Path = typer.Argument(Path.cwd(), exists=True),
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    Config.verbose = verbose
    n, time = add_exif(directory)
    print(f"Added EXIF data to {n} images in {time:.2f}s")


@app.command(help="Get EXIF data from an image")
def get(image: Path = typer.Argument(..., exists=True)) -> None:
    print_table(get_exif_from_image(image))


@app.command(help="Check if all images in a directory have EXIF data")
def check(
    directory: Path = typer.Argument(Path.cwd(), exists=True),
    recursive: Annotated[bool, typer.Option("--recursive", "-R")] = False,
    list: Annotated[bool, typer.Option("--list", "-l")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    Config.verbose = verbose
    y, n = get_exif(directory, recursive)

    print(f"{len(y):>4} - \u2705 EXIF")
    print(f"{len(n):>4} - \u274C EXIF")

    if list:
        for img in sorted(n):
            print("\u274c", img)

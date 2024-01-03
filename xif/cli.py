from pathlib import Path

import typer
from typing_extensions import Annotated

from xif.main import ImageDir, add_exif, get_exif

app = typer.Typer()


@app.command(help="Add EXIF data to an image")
def add(
    directory: Path = typer.Argument(Path.cwd(), exists=True),
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    id = ImageDir(directory)
    for img in id.images:
        add_exif(img, id.image_exif(img), print_=verbose)


@app.command(help="Get EXIF data from an image")
def get(image: Path = typer.Argument(..., exists=True)) -> None:
    data = get_exif(image)
    key_len = max(len(key) for key in data.keys())
    for key, value in data.items():
        print(f"{key + ':':.<{key_len}} {value}")


@app.command(help="Check if all images in a directory have EXIF data")
def check(
    directory: Path = typer.Argument(Path.cwd(), exists=True),
    recursive: Annotated[bool, typer.Option("--recursive", "-R")] = False,
    list: Annotated[bool, typer.Option("--list", "-l")] = False,
) -> None:
    y = set()
    n = set()

    func = directory.rglob if recursive else directory.glob
    for img in func("*.png"):
        try:
            get_exif(img)
            y.add(img)
        except KeyError:
            n.add(img)

    print(f"{len(y):>4} - \u2705 EXIF")
    print(f"{len(n):>4} - \u274C EXIF")

    if list:
        for img in sorted(n):
            print("\u274c", img)

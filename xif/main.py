import json
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from PIL import Image

from xif.config import Config


class ImageDir:
    data: dict[str, dict[str, str]] = dict()

    def __init__(self, directory: Path) -> None:
        self.location = directory
        self.parse_log()

    def __str__(self) -> str:
        return self.location

    def __repr__(self) -> str:
        return f"ImageDir({self.location})"

    @property
    def log(self) -> Path:
        return self.location / "log.html"

    @property
    def images(self) -> list[Path]:
        return list(self.location.glob("*.png"))

    def parse_log(self) -> None:
        soup = BeautifulSoup(self.log.read_text(), "html.parser")

        for record in soup.find_all("div", class_="image-container"):
            record_data = dict()
            filename = record.find("img")["src"]

            metadata = record.find("table", class_="metadata").find_all("tr")
            for row in metadata:
                key, value = row.find_all("td")
                record_data[key.text.strip().replace(" ", "_")] = value.text.strip()

            self.data[filename] = record_data

    def image_exif(self, image: Path) -> dict[str, Any]:
        return self.data[image.name]


def add_exif_to_image(
    image: Path,
    exif_data: dict,
    output_dir: Path = None,
) -> None:
    if not image.exists():
        return
    if output_dir is None:
        output_dir = image.parent
    if Config.VERBOSE:
        print(image)

    im = Image.open(image)
    exif = im.getexif()
    exif[Config.EXIF_FIELD] = json.dumps(exif_data)
    im.save(output_dir / image.name, exif=exif)


def get_exif_from_image(image: Path) -> dict:
    if Config.VERBOSE:
        print(image)
    im = Image.open(image)
    exif = im.getexif()
    return json.loads(exif[Config.EXIF_FIELD])


def add_exif(directory: Path) -> tuple[int, float]:
    id = ImageDir(directory)
    start = time.perf_counter()

    for img in id.images:
        add_exif_to_image(img, id.image_exif(img))

    return len(id.images), time.perf_counter() - start


def get_exif(directory: Path, recursive: bool = False) -> tuple[set, set]:
    y = set()
    n = set()

    func = directory.rglob if recursive else directory.glob
    for img in func("*.png"):
        try:
            get_exif_from_image(img)
            y.add(img)
        except KeyError:
            n.add(img)

    return y, n

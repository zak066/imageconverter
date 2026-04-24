import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Optional


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
    ".avif",
    ".gif",
    ".heic",
    ".heif",
}

RESAMPLE_METHODS = {
    "LANCZOS": 0,
    "BICUBIC": 2,
    "BILINEAR": 1,
    "NEAREST": 3,
}


@dataclass
class Dimensions:
    large: int = 1200
    medium: int = 800
    small: int = 400
    x_small: int = 200


@dataclass
class Config:
    dimensions: Dimensions = None
    output_format: str = "webp"
    quality: int = 90
    output_folder: Optional[str] = None
    prefix: str = ""
    overwrite: bool = False
    skip_existing: bool = True
    resample_method: str = "LANCZOS"
    input_extensions: List[str] = field(
        default_factory=lambda: [
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".tif",
            ".webp",
            ".avif",
        ]
    )
    generate_sizes: List[str] = field(
        default_factory=lambda: ["original", "large", "medium", "small", "x_small"]
    )

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = Dimensions()
        if not self.input_extensions:
            self.input_extensions = [
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
                ".tiff",
                ".tif",
                ".webp",
                ".avif",
            ]
        if not self.generate_sizes:
            self.generate_sizes = ["original", "large", "medium", "small", "x_small"]


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path.home() / ".imgconverter" / "config.json"
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = Config()
        self.load()

    def load(self) -> Config:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    dims = Dimensions(**data.get("dimensions", {}))
                    self._config = Config(
                        dimensions=dims,
                        output_format=data.get("output_format", "webp"),
                        quality=data.get("quality", 90),
                        output_folder=data.get("output_folder"),
                        prefix=data.get("prefix", ""),
                        overwrite=data.get("overwrite", False),
                        skip_existing=data.get("skip_existing", True),
                        resample_method=data.get("resample_method", "LANCZOS"),
                        input_extensions=data.get(
                            "input_extensions",
                            [
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".bmp",
                                ".tiff",
                                ".tif",
                                ".webp",
                                ".avif",
                            ],
                        ),
                        generate_sizes=data.get(
                            "generate_sizes",
                            ["original", "large", "medium", "small", "x_small"],
                        ),
                    )
            except (json.JSONDecodeError, KeyError):
                self._config = Config()
        return self._config

    def save(self, config: Config = None):
        if config is None:
            config = self._config
        data = {
            "dimensions": asdict(config.dimensions),
            "output_format": config.output_format,
            "quality": config.quality,
            "output_folder": config.output_folder,
            "prefix": config.prefix,
            "overwrite": config.overwrite,
            "skip_existing": config.skip_existing,
            "resample_method": config.resample_method,
            "input_extensions": config.input_extensions,
            "generate_sizes": config.generate_sizes,
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_config(self, path: str):
        path = Path(path)
        data = {
            "dimensions": asdict(self._config.dimensions),
            "output_format": self._config.output_format,
            "quality": self._config.quality,
            "output_folder": self._config.output_folder,
            "prefix": self._config.prefix,
            "overwrite": self._config.overwrite,
            "skip_existing": self._config.skip_existing,
            "resample_method": self._config.resample_method,
            "input_extensions": self._config.input_extensions,
            "generate_sizes": self._config.generate_sizes,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def import_config(self, path: str):
        path = Path(path)
        if path.exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    dims = Dimensions(**data.get("dimensions", {}))
                    self._config = Config(
                        dimensions=dims,
                        output_format=data.get("output_format", "webp"),
                        quality=data.get("quality", 90),
                        output_folder=data.get("output_folder"),
                        prefix=data.get("prefix", ""),
                        overwrite=data.get("overwrite", False),
                        skip_existing=data.get("skip_existing", True),
                        resample_method=data.get("resample_method", "LANCZOS"),
                        input_extensions=data.get(
                            "input_extensions",
                            [
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".bmp",
                                ".tiff",
                                ".tif",
                                ".webp",
                                ".avif",
                            ],
                        ),
                        generate_sizes=data.get(
                            "generate_sizes",
                            ["original", "large", "medium", "small", "x_small"],
                        ),
                    )
                    self.save()
            except (json.JSONDecodeError, KeyError):
                pass

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config):
        self._config = value
        self.save()


def get_image_files(path: str, extensions: List[str] = None) -> List[Path]:
    path = Path(path)
    files = []
    exts = extensions or [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".avif",
    ]

    if path.is_file():
        if path.suffix.lower() in exts:
            files.append(path)
    elif path.is_dir():
        for ext in exts:
            files.extend(path.glob(f"*{ext}"))
            files.extend(path.glob(f"*{ext.upper()}"))

    return sorted(files)


def scale_width(image_width: int, target_width: int) -> tuple:
    aspect_ratio = image_width / image_width
    target_height = int(image_width * aspect_ratio)
    return (target_width, target_height)


def get_image_dimensions(path: Path) -> tuple:
    from PIL import Image

    with Image.open(path) as img:
        return img.size

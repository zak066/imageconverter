import os
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


SUPPORTED_FORMATS = ["webp", "avif"]


class ImageConverter:
    def __init__(
        self,
        source_dir: Path,
        output_format: str = "webp",
        dimensions: dict = None,
        quality: int = 90,
        output_folder: Optional[Path] = None,
        prefix: str = "",
        overwrite: bool = False,
        skip_existing: bool = True,
        resample_method: str = "LANCZOS",
        progress_callback: Optional[Callable] = None,
    ):
        self.source_dir = Path(source_dir)
        self.output_format = output_format.lower()
        self.quality = quality
        self.output_folder = Path(output_folder) if output_folder else None
        self.prefix = prefix
        self.overwrite = overwrite
        self.skip_existing = skip_existing
        self.resample_method = resample_method
        self.progress_callback = progress_callback
        self._cancel = False
        self._lock = threading.Lock()
        self.dimensions = dimensions or {
            "large": 1200,
            "medium": 800,
            "small": 400,
            "x_small": 200,
        }
        self._resample = getattr(
            Image.Resampling, resample_method, Image.Resampling.LANCZOS
        )

    def cancel(self):
        self._cancel = True

    def _should_convert(self, output_path: Path) -> bool:
        if not output_path.exists():
            return True
        if self.overwrite:
            return True
        if self.skip_existing:
            return False
        return True

    def _get_output_path(
        self, base_name: str, suffix: Optional[str], output_dir: Path
    ) -> Path:
        if self.prefix:
            base_name = f"{self.prefix}{base_name}"
        if suffix:
            suffix = suffix.replace("_", "-")
        ext = "avif" if self.output_format == "avif" else "webp"
        return output_dir / f"{base_name}{f'-{suffix}' if suffix else ''}.{ext}"

    def convert(
        self, progress_callback: Optional[Callable] = None
    ) -> List[Tuple[str, bool, str]]:
        if progress_callback:
            self.progress_callback = progress_callback

        image_files = self._get_image_files()
        results = []
        total = len(image_files)
        completed = 0

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._convert_single, f): f for f in image_files}
            for future in as_completed(futures):
                if self._cancel:
                    executor.shutdown(wait=False)
                    break
                result = future.result()
                results.append(result)
                completed += 1
                if self.progress_callback:
                    self.progress_callback(
                        (completed / total) * 100, result[0], result[1]
                    )

        return results

    def _get_image_files(self):
        from config import get_image_files

        return get_image_files(self.source_dir)

    def _convert_single(self, image_path: Path) -> Tuple[str, bool, str]:
        try:
            with Image.open(image_path) as img:
                original_width = img.size[0]
                base_name = image_path.stem

                output_dir = (
                    self.output_folder if self.output_folder else image_path.parent
                )
                output_dir.mkdir(parents=True, exist_ok=True)

                error_msg = ""
                converted = 0

                out_path = self._get_output_path(base_name, None, output_dir)
                if self._should_convert(out_path):
                    self._save_image(img, original_width, base_name, output_dir, None)
                    converted += 1

                for suffix, target_width in self.dimensions.items():
                    if self._cancel:
                        break
                    out_path = self._get_output_path(base_name, suffix, output_dir)
                    if self._should_convert(out_path):
                        resized = self._resize_image(img, target_width)
                        self._save_image(
                            resized, target_width, base_name, output_dir, suffix
                        )
                        converted += 1

                return (image_path.name, True, f"Convertiti {converted} file")
        except Exception as e:
            return (image_path.name, False, str(e))

    def _resize_image(self, img: Image.Image, target_width: int) -> Image.Image:
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        target_height = int(target_width * aspect_ratio)
        return img.resize((target_width, target_height), self._resample)

    def _save_image(
        self,
        img: Image.Image,
        width: int,
        base_name: str,
        output_dir: Path,
        suffix: Optional[str],
    ) -> Path:
        save_path = self._get_output_path(base_name, suffix, output_dir)
        if self.output_format == "avif":
            img.save(save_path, "AVIF", quality=self.quality)
        else:
            img.save(save_path, "WEBP", quality=self.quality)
        return save_path


def convert_files(
    source_dir: Path,
    output_format: str = "webp",
    dimensions: dict = None,
    quality: int = 90,
    output_folder: Optional[Path] = None,
    prefix: str = "",
    overwrite: bool = False,
    skip_existing: bool = True,
    resample_method: str = "LANCZOS",
    progress_callback: Optional[Callable] = None,
) -> List[Tuple[str, bool, str]]:
    converter = ImageConverter(
        source_dir,
        output_format,
        dimensions,
        quality,
        output_folder,
        prefix,
        overwrite,
        skip_existing,
        resample_method,
        progress_callback,
    )
    return converter.convert()

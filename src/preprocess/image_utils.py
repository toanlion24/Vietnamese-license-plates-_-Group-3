"""
Tiền xử lý ảnh cơ bản: đọc, resize, chỉnh sáng/tương phản, xoay nhẹ.
Dùng cho thử nghiệm / pipeline tùy chỉnh; YOLOv8 vẫn có augment nội bộ khi train.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image_bgr(path: str | Path) -> np.ndarray:
    p = Path(path)
    img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {p}")
    return img


def save_image_bgr(path: str | Path, image: np.ndarray) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower() or ".png"
    ok, buf = cv2.imencode(ext, image)
    if not ok:
        raise RuntimeError(f"encode failed: {p}")
    buf.tofile(str(p))


def resize_to_max_side(image: np.ndarray, max_side: int, interpolation: int = cv2.INTER_AREA) -> np.ndarray:
    h, w = image.shape[:2]
    m = max(h, w)
    if m <= max_side:
        return image
    scale = max_side / m
    nw, nh = int(w * scale), int(h * scale)
    return cv2.resize(image, (nw, nh), interpolation=interpolation)


def resize_to(image: np.ndarray, width: int, height: int, interpolation: int = cv2.INTER_AREA) -> np.ndarray:
    return cv2.resize(image, (width, height), interpolation=interpolation)


def adjust_brightness_contrast(
    image: np.ndarray,
    alpha: float = 1.0,
    beta: float = 0.0,
) -> np.ndarray:
    """
    alpha: hệ số tương phản (nhân).
    beta: độ sáng (cộng), thường -40..40.
    """
    out = np.clip(image.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
    return out


def rotate_degrees(
    image: np.ndarray,
    angle: float,
    border_value: tuple[int, int, int] = (114, 114, 114),
) -> np.ndarray:
    """Xoay quanh tâm ảnh, góc độ (dương = ngược chiều kim đồng hồ)."""
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image,
        m,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )


def random_light_augment(
    image: np.ndarray,
    alpha_range: tuple[float, float] = (0.85, 1.15),
    beta_range: tuple[float, float] = (-25.0, 25.0),
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    a = float(rng.uniform(*alpha_range))
    b = float(rng.uniform(*beta_range))
    return adjust_brightness_contrast(image, alpha=a, beta=b)


def random_small_rotation(
    image: np.ndarray,
    max_abs_deg: float = 8.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    angle = float(rng.uniform(-max_abs_deg, max_abs_deg))
    return rotate_degrees(image, angle)

import cv2
import numpy as np
from pathlib import Path

def image_to_complex_points(image_path: Path, max_points: int):
    """
    Convert an image into a Fourier-ready complex64 numpy array.

    Parameters:
        image_path (str): path to image file
        max_points (int): optional downsampling limit

    Returns:
        np.ndarray: complex64 array of shape (N,)
    """

    # ----------------------------
    # 1. Load grayscale image
    # ----------------------------
    img = cv2.imread(image_path, 0)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # ----------------------------
    # 2. Preprocess
    # ----------------------------
    blur = cv2.GaussianBlur(img, (5, 5), 0)

    _, thresh = cv2.threshold(
        blur, 127, 255, cv2.THRESH_BINARY_INV
    )

    # Clean small noise
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # ----------------------------
    # 3. Extract contours
    # ----------------------------
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    if not contours:
        raise ValueError("No contours found in image.")

    # Largest contour = main shape
    cnt = max(contours, key=cv2.contourArea)

    # ----------------------------
    # 4. Convert to points
    # ----------------------------
    pts = cnt[:, 0, :].astype(np.float64)

    x = pts[:, 0]
    y = pts[:, 1]

    # ----------------------------
    # 5. Centering (important for Fourier)
    # ----------------------------
    x -= np.mean(x)
    y -= np.mean(y)

    # Normalize scale
    scale = np.max(np.sqrt(x**2 + y**2))
    if scale != 0:
        x /= scale
        y /= scale

    # ----------------------------
    # 6. Complex signal
    # ----------------------------
    z = x + 1j * -y

    # Close loop (important for drawing continuity)
    z = np.append(z, z[0])

    # ----------------------------
    # 7. Downsample (speed control)
    # ----------------------------
    if len(z) > max_points:
        step = len(z) // max_points
        z = z[::step]

    # ----------------------------
    # 8. Convert dtype
    # ----------------------------
    return z.astype(np.complex64)



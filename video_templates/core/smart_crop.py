"""
smart_crop.py - AI Subject Tracking & Dynamic Auto-Framing Engine.
Detects faces and visual saliency in source video to dynamically calculate
optimal crop windows when reframing 16:9 landscape footage into 9:16 portrait.
"""

from pathlib import Path
import cv2
import numpy as np


_FACE_CASCADE = None


def get_face_cascade():
    """Lazily load the OpenCV Haar face cascade classifier."""
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def analyze_frame_focal_x(frame):
    """
    Analyzes a single BGR video frame to detect the primary subject center X (0.0 to 1.0).
    Uses face detection as highest priority, falling back to visual gradient saliency.
    """
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1. Face Detection Priority
    face_cascade = get_face_cascade()
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=4,
        minSize=(int(h * 0.08), int(h * 0.08))
    )

    if len(faces) > 0:
        # Weight faces by bounding box area (largest face = most prominent subject)
        total_weight = 0.0
        weighted_center_x = 0.0
        for (fx, fy, fw, fh) in faces:
            area = float(fw * fh)
            cx = fx + fw / 2.0
            weighted_center_x += cx * area
            total_weight += area
        if total_weight > 0:
            return float((weighted_center_x / total_weight) / w)

    # 2. Visual Saliency / Center-of-Mass via Sobel Gradients
    # Computes visual contrast & edges across the horizontal axis
    small = cv2.resize(gray, (160, 90), interpolation=cv2.INTER_AREA)
    sobel_x = cv2.Sobel(small, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(small, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(sobel_x**2 + sobel_y**2)

    # Weight towards the center of frame slightly to prevent pulling towards edge artifacts
    x_indices = np.linspace(0.0, 1.0, small.shape[1])
    col_weights = np.mean(mag, axis=0)
    center_bias = 1.0 - 0.3 * np.abs(x_indices - 0.5)
    biased_weights = col_weights * center_bias

    total_weight = np.sum(biased_weights)
    if total_weight > 1e-5:
        focal_x = float(np.sum(x_indices * biased_weights) / total_weight)
        return focal_x

    # Fallback to absolute center
    return 0.5


def calculate_smart_crop(src_path, start, end, orig_w, orig_h, target_w, target_h, num_samples=6):
    """
    Analyzes video segment to find the optimal horizontal crop offset.
    Returns:
      crop_x_start: normalized crop offset (0.0 to 1.0)
      crop_x_end: normalized crop offset at end of clip for smooth dynamic pan
    """
    # Calculate aspect ratios
    orig_aspect = orig_w / float(orig_h)
    target_aspect = target_w / float(target_h)

    # If already same or narrower aspect, center crop is optimal
    if orig_aspect <= target_aspect + 0.05:
        return 0.5, 0.5

    cap = cv2.VideoCapture(str(src_path))
    if not cap.isOpened():
        return 0.5, 0.5

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    start_frame = int(start * fps)
    end_frame = int(end * fps)
    total_frames = max(1, end_frame - start_frame)

    sample_indices = np.linspace(start_frame, end_frame - 1, num_samples).astype(int)
    focal_points = []

    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret and frame is not None:
            focal_x = analyze_frame_focal_x(frame)
            focal_points.append(focal_x)

    cap.release()

    if not focal_points:
        return 0.5, 0.5

    # Smooth the focal points across time
    focal_points = np.array(focal_points)
    focal_start = float(np.mean(focal_points[:len(focal_points)//2]))
    focal_end = float(np.mean(focal_points[len(focal_points)//2:]))

    # Clamp the camera pan range so it doesn't move too violently
    max_pan_drift = 0.12
    if abs(focal_end - focal_start) > max_pan_drift:
        focal_end = focal_start + np.sign(focal_end - focal_start) * max_pan_drift

    return round(focal_start, 3), round(focal_end, 3)


def get_crop_filter_expression(orig_w, orig_h, target_w, target_h, focal_start, focal_end, dur):
    """
    Builds an FFmpeg crop expression that smoothly pans from focal_start to focal_end.
    """
    orig_aspect = orig_w / float(orig_h)
    target_aspect = target_w / float(target_h)

    if orig_aspect <= target_aspect:
        # Scale to height and center crop
        return f"crop={target_w}:{target_h}:(iw-ow)/2:(ih-oh)/2"

    # Width needed to preserve aspect ratio
    # After scale=target_w:target_h:force_original_aspect_ratio=increase
    # scaled height = target_h, scaled width = target_h * orig_aspect
    scaled_w = int(target_h * orig_aspect)
    max_x = max(0, scaled_w - target_w)

    x_start = int(np.clip(focal_start * scaled_w - target_w / 2.0, 0, max_x))
    x_end = int(np.clip(focal_end * scaled_w - target_w / 2.0, 0, max_x))

    if abs(x_end - x_start) <= 10 or dur <= 0.1:
        # Static smart crop position
        return f"crop={target_w}:{target_h}:{x_start}:(ih-oh)/2"
    else:
        # Smooth dynamic pan across the clip duration
        pan_expr = f"{x_start}+({x_end}-{x_start})*(t/{dur:.3f})"
        return f"crop={target_w}:{target_h}:'min({max_x},max(0,{pan_expr}))':(ih-oh)/2"

import cv2
from typing import List


def save_last_frame(video_path: str, output_path: str) -> bool:
    """
    Extract the last frame of an mp4 video and save it as a PNG.

    Args:
        video_path: Path to the input .mp4 file.
        output_path: Path where the .png will be saved.

    Returns:
        True if a frame was saved successfully, False otherwise.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise IOError(f"Could not open video file: {video_path}")

    last_frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        last_frame = frame

    cap.release()

    if last_frame is None:
        print("No frames could be read from the video.")
        return False

    cv2.imwrite(output_path, last_frame)
    return True


def save_last_frames(video_paths: List[str], output_paths: List[str]) -> List[bool]:
    """
    Extract the last frame from multiple mp4 videos and save each as a PNG.

    Args:
        video_paths: List of paths to input .mp4 files.
        output_paths: List of paths where each .png will be saved.
                       Must be the same length as video_paths, and
                       output_paths[i] corresponds to video_paths[i].

    Returns:
        List of booleans indicating success/failure for each video,
        in the same order as the inputs.
    """
    if len(video_paths) != len(output_paths):
        raise ValueError(
            f"video_paths and output_paths must be the same length "
            f"({len(video_paths)} != {len(output_paths)})"
        )

    results = []
    for video_path, output_path in zip(video_paths, output_paths):
        try:
            success = save_last_frame(video_path, output_path)
        except IOError as e:
            print(f"Error processing {video_path}: {e}")
            success = False
        results.append(success)

    return results



videos = [
"obliqueShocks/Videos/M12.mp4",
"obliqueShocks/Videos/M14.mp4",
"obliqueShocks/Videos/M16.mp4",
"obliqueShocks/Videos/M18.mp4",
"obliqueShocks/Videos/M20.mp4",
"obliqueShocks/Videos/M22.mp4",
"obliqueShocks/Videos/M24.mp4",
"obliqueShocks/Videos/M26.mp4"
]
outputs = [
    "obliqueShocks/Videos/last1.png",
    "obliqueShocks/Videos/last2.png",
    "obliqueShocks/Videos/last3.png",
    "obliqueShocks/Videos/last4.png",
    "obliqueShocks/Videos/last5.png",
    "obliqueShocks/Videos/last6.png",
    "obliqueShocks/Videos/last7.png",
    "obliqueShocks/Videos/last8.png"
]

results = save_last_frames(videos, outputs)

import hashlib

from .image import ffmpeg_rawvideo_to_gif
from .image import ffmpeg_rawvideo_to_video
from .image import catenate_images

def hash(value: str) -> str:
  return hashlib.sha256(value.encode()).hexdigest()

def uclamp(x):
  return max(0, min(1, x))

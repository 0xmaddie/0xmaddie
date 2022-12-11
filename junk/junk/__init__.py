import hashlib

# import junk.nn
import junk.lisp
import junk.pil
import junk.ffmpeg
import junk.random
# import junk.turtle_graphics
import junk.sdm_2022_11

def hash(value: str) -> str:
  return hashlib.sha256(value.encode()).hexdigest()

def uclamp(x):
  return max(0, min(1, x))

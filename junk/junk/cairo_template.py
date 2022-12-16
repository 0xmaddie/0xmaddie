import sys
import time
import math
import dataclasses
import functools as fn
import numpy as np
import cairo

from typing import Tuple
from typing import Callable
from typing import Generator

if __name__ == '__main__':
  WIDTH = 1024
  HEIGHT = 1024
  surface = cairo.ImageSurface(
    cairo.FORMAT_ARGB32,
    WIDTH,
    HEIGHT,
  )
  ctx = cairo.Context(surface)

  ctx.save()
  ctx.translate(WIDTH/2, HEIGHT/2)
  ctx.scale(WIDTH/2, HEIGHT/2)

  ctx.set_source_rgb(0.0, 0.0, 0.0)
  ctx.paint()

  ctx.set_source_rgb(1.0, 1.0, 1.0)
  ctx.arc(0, 0, 1, 0, 2*math.pi)
  ctx.fill()

  ctx.restore()

  surface.write_to_png(f'cairo_template_{int(time.time())}.png')

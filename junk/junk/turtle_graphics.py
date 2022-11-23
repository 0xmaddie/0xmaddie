import PIL
import cairo

import junk.nn
import junk.pil

class Turtle:
  width: int
  height: int
  def __init__(
    self,
    width: int  = 512,
    height: int = 512,
  ):
    self.width  = width
    self.height = height

  def __call__(self, code: str) -> PIL.Image:
    weights = junk.nn.use_weights((6,))
    surface = cairo.ImageSurface(
      cairo.FORMAT_ARGB32,
      self.width,
      self.height,
    )
    ctx = cairo.Context(surface)
    ctx.save()
    ctx.translate(self.width/2, self.height/2)
    ctx.scale(self.width/2, self.height/2)
    is_pen_down = False
    for token in code:
      if token == ' ':
        pass
      elif token == '[':
        ctx.save()
      elif token == ']':
        ctx.restore()
      elif token == 'r':
        pass
      elif token == 'R':
        pass
      elif token == 's':
        pass
      elif token == 'S':
        pass
      elif token == 't':
        pass
      elif token == 'T':
        pass
      elif token == 'u':
        is_pen_down = False
      elif token == 'U':
        is_pen_down = True
      elif token == 'v':
        pass
      elif token == 'V':
        pass
      else:
        pass
    ctx.restore()
    image = junk.pil.from_cairo(surface)
    return image

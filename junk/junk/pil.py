import PIL
import cairo

def cat(images, rows, cols):
  assert len(images) == rows*cols

  width, height = images[0].size
  grid = PIL.Image.new(
    'RGB',
    size=(cols*width, rows*height),
  )

  for index, image in enumerate(images):
    box = (index%cols*width, index//cols*height)
    grid.paste(image, box=box)

  return grid

def from_cairo(
  sx: cairo.ImageSurface,
):
  image = PIL.Image.frombuffer(
    'RGBA',
    (sx.get_width(), sx.get_height()),
    sx.get_data().tobytes(),
    'raw',
    'BGRA',
    sx.get_stride(),
  )
  return image

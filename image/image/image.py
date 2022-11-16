import os
import PIL
import IPython

def ffmpeg_rawvideo_to_gif(
  source: str    = 'source.raw',
  target: str    = 'target.gif',
  height: int    = 512,
  width: int     = 512,
  framerate: int = 15,
):
  parts = [
    f'ffmpeg',
    f'-f rawvideo',
    f'-pix_fmt bgra',
    f'-r {framerate}',
    f'-s {width}x{height}',
    f'-i {source}',
    f'{target}',
  ]
  command = ' '.join(parts)
  os.system(command)
  image = IPython.display.Image(filename=target)
  return image

def ffmpeg_rawvideo_to_video(
  source: str    = 'source.raw',
  target: str    = 'target.webm',
  height: int    = 512,
  width: int     = 512,
  framerate: int = 15,
):
  parts = [
    f'ffmpeg',
    f'-f rawvideo',
    f'-pix_fmt bgra',
    f'-r {framerate}',
    f'-s {width}x{height}',
    f'-i {source}',
    f'-pix_fmt yuv420p',
    f'{target}',
  ]
  command = ' '.join(parts)
  os.system(command)
  video = IPython.display.Video(target, embed=True)
  return video

def catenate_images(images, rows, cols):
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

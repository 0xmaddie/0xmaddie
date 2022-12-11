import dataclasses
from typing import List
from typing import Any
from typing import Optional

class Command:
  pass

@dataclasses.dataclass(frozen=True)
class Draw(Command):
  prompt: str
  coprompt: Optional[str] = None
  batch_size: int = 4
  guidance_scale: float = 13.0
  num_inference_steps: int = 50
  initial_image: Optional[str] = None
  image_denoise_strength: float = 0.7

@dataclasses.dataclass(frozen=True)
class Choice(Command):
  values: List[Any]

class Model:
  def __call__(self, prompt):
    try:
      cmd = next(prompt)
      while True:
        if isinstance(cmd, DrawImage):
          pass
        elif isinstance(cmd, Choice):
          pass
        else:
          pass
    except StopIteration as stop:
      pass

def draw(prompt: str) -> Command:
  return Draw(prompt)

def cat(xs: list[str]) -> str:
  return ', '.join(xs)

def example_prompt():
  prompt = [
    
  ]
  sort = yield choice(['a japanese', 'a korean'])
  prompt.append(sort)
  prompt.append('woman posing for a picture')
  yield draw(cat(prompt))
  artists = yield choice([
    'by ilya kuvshinov',
    'by greg rutkowski',
    'by john singer sargent',
  ])
  prompt.extend(artists)
  yield draw(cat(prompt))

from typing import Tuple
# from typing import Union
from typing import Optional
from typing import List
# from typing import Sequence
# from typing import Callable
from typing import Any

from dataclasses import dataclass

def _normalize_filter(filter):
  # if isinstance(filter, list):
  if not isinstance(filter, str):
    filter = [x for x in filter if len(x) > 0]
    filter = ' '.join(filter)
  return filter

RandomSeed = Tuple[str, int]

_sdm_prompt_context = None

class SdmPromptContext:
  filters: List[str]
  size: Tuple[int, int] = (512, 512)
  random_seed: RandomSeed = ('pin', 0)
  guidance_scale: int = 13.0
  num_inference_steps: int = 50
  initial_image: Optional[str] = None
  image_denoise_strength: float = 0.7

  def __init__(self):
    self.filters = []

  @property
  def prompt(self) -> str:
    # return ','.join(self.filters)
    return ', '.join(self.filters)

  def __enter__(self):
    global _sdm_prompt_context
    assert _sdm_prompt_context is None
    _sdm_prompt_context = self
    return self

  def __exit__(self, kind, err, traceback):
    global _sdm_prompt_context
    assert _sdm_prompt_context is self
    _sdm_prompt_context = None
    return False

  def push(self, filter):
    filter = _normalize_filter(filter)
    if len(filter) > 0:
      self.filters.append(filter)

  def has(self, filter):
    filter = _normalize_filter(filter)
    return filter in self.filters
  
def push(filter):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  return _sdm_prompt_context.push(filter)

def has(filter):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  return _sdm_prompt_context.has(filter)

def set_random_seed(value: RandomSeed):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  _sdm_prompt_context.random_seed = value

def set_num_inference_steps(value: int):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  _sdm_prompt_context.num_interfence_steps = value

def set_guidance_scale(value: int):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  _sdm_prompt_context.guidance_scale = value

def set_image_denoise_strength(value: float):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  _sdm_prompt_context.image_denoise_strength = value

def set_initial_image(value: str):
  global _sdm_prompt_context
  assert _sdm_prompt_context is not None
  _sdm_prompt_context.initial_image = value
  
@dataclass(frozen=True)
class SdmPromptResult:
  images: List[Any]
  prompt: str = ''
  random_seed: Tuple[str, int] = ('pin', 0)
  guidance_scale: float = 13.0
  num_inference_steps: int = 50
  created_time: int = 0
  initial_image: Optional[str] = None
  image_denoise_strength: float = 0.7

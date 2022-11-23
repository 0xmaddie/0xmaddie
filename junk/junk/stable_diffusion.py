import sys
import time
import torch
import PIL
import diffusers as ds
from loguru import logger as log

import junk

from dataclasses import dataclass

from typing import Tuple
# from typing import Union
from typing import Optional
from typing import List
# from typing import Sequence
# from typing import Callable
from typing import Any

def _normalize_filter(filter):
  # if isinstance(filter, list):
  if not isinstance(filter, str):
    filter = [x for x in filter if len(x) > 0]
    filter = ' '.join(filter)
  return filter

RandomSeed = Tuple[str, int]

_prompt_context = None

class PromptContext:
  filters: List[str]
  size: Tuple[int, int] = (512, 512)
  random_seed: RandomSeed = ('pin', 0)
  guidance_scale: float = 13.0
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
    global _prompt_context
    # assert _prompt_context is None
    _prompt_context = self
    return self

  def __exit__(self, kind, err, traceback):
    global _prompt_context
    assert _prompt_context is self
    _prompt_context = None
    return False

  def push(self, filter):
    filter = _normalize_filter(filter)
    if len(filter) > 0:
      self.filters.append(filter)

  def has(self, filter):
    filter = _normalize_filter(filter)
    return filter in self.filters
  
def push(filter):
  global _prompt_context
  assert _prompt_context is not None
  return _prompt_context.push(filter)

def has(filter):
  global _prompt_context
  assert _prompt_context is not None
  return _prompt_context.has(filter)

def set_random_seed(value: RandomSeed):
  global _prompt_context
  assert _prompt_context is not None
  _prompt_context.random_seed = value

def set_num_inference_steps(value: int):
  global _prompt_context
  assert _prompt_context is not None
  _prompt_context.num_inference_steps = value

def set_guidance_scale(value: int):
  global _prompt_context
  assert _prompt_context is not None
  _prompt_context.guidance_scale = value

def set_image_denoise_strength(value: float):
  global _prompt_context
  assert _prompt_context is not None
  _prompt_context.image_denoise_strength = value

def set_initial_image(value: str):
  global _prompt_context
  assert _prompt_context is not None
  _prompt_context.initial_image = value

@dataclass(frozen=True)
class PromptResult:
  images: List[Any]
  prompt: str = ''
  random_seed: Tuple[str, int] = ('pin', 0)
  guidance_scale: float = 13.0
  num_inference_steps: int = 50
  session_id: int = 0
  batch_id: int = 0
  initial_image: Optional[str] = None
  image_denoise_strength: float = 0.7

class Model:
  text_to_image_pipeline: ds.DiffusionPipeline
  image_to_image_pipeline: ds.DiffusionPipeline
  finetuned_vae: ds.AutoencoderKL
  torch_rng: torch.Generator

  def __init__(self, path: str):
    self.torch_rng = torch.Generator('cuda')

    self.finetuned_vae = ds.models.AutoencoderKL.from_pretrained(
      'stabilityai/sd-vae-ft-ema',
      cache_dir = path,
    )

    self.text_to_image_pipeline = ds.StableDiffusionPipeline.from_pretrained(
      'runwayml/stable-diffusion-v1-5',
      revision         = 'fp16',
      torch_dtype      = torch.float16,
      # use_auth_token = True,
      local_files_only = True,
      cache_dir        = path,
      vae              = self.finetuned_vae,
      safety_checker   = None,
    ).to('cuda')

    self.text_to_image_pipeline.enable_attention_slicing()
    
    self.image_to_image_pipeline = ds.StableDiffusionImg2ImgPipeline(
      vae               = self.text_to_image_pipeline.vae,
      text_encoder      = self.text_to_image_pipeline.text_encoder,
      tokenizer         = self.text_to_image_pipeline.tokenizer,
      unet              = self.text_to_image_pipeline.unet,
      scheduler         = self.text_to_image_pipeline.scheduler,
      feature_extractor = self.text_to_image_pipeline.feature_extractor,
      # safety_checker    = self.text_to_image_pipeline.safety_checker,
      safety_checker    = None,
    )

    self.image_to_image_pipeline.enable_attention_slicing()

    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss zz}</green> · <level>{message}</level>"
    log.remove()
    log.add(sys.stderr, level='TRACE', format=log_format)
    log.add(f'{path}/log', level='INFO', format=log_format)
    log.success('connected')

  def generate(self, prompt_fn, batch_size, iterations):
    session_id = int(time.time())
    log.info(f'session_{session_id}()')
    log.info(f'session_{session_id}.batch_size = {batch_size}')
    log.info(f'session_{session_id}.iterations = {iterations}')

    image_cache = {}
    def get_image(path):
      if not path in image_cache:
        image_cache[path] = PIL.Image.open(path).convert('RGB')
      return image_cache[path]

    pinned_seed_value = None

    for batch_id in range(iterations):
      with PromptContext() as prompt_context:
        prompt_fn()

        seed_type, seed_value = prompt_context.random_seed
        if seed_type == 'pin':
          if batch_id == 0:
            pinned_seed_value = seed_value
            self.torch_rng.manual_seed(seed_value)
          else:
            assert pinned_seed_value == seed_value
        else:
          assert seed_type == 'set'
          assert pinned_seed_value == None
          self.torch_rng.manual_seed(seed_value)

        prompt                 = prompt_context.prompt
        size                   = prompt_context.size
        random_seed            = prompt_context.random_seed
        guidance_scale         = prompt_context.guidance_scale
        num_inference_steps    = prompt_context.num_inference_steps
        initial_image          = prompt_context.initial_image
        image_denoise_strength = prompt_context.image_denoise_strength

      log.info(f'session_{session_id}_{batch_id}()')
      log.info(f'session_{session_id}_{batch_id}.prompt                 = {prompt}')
      log.info(f'session_{session_id}_{batch_id}.prompt.len             = {len(prompt)}')
      log.info(f'session_{session_id}_{batch_id}.prompt.hash            = {junk.hash(prompt)}')
      log.info(f'session_{session_id}_{batch_id}.size                   = {size}')
      log.info(f'session_{session_id}_{batch_id}.random_seed            = {random_seed}')
      log.info(f'session_{session_id}_{batch_id}.guidance_scale         = {guidance_scale}')
      log.info(f'session_{session_id}_{batch_id}.num_inference_steps    = {num_inference_steps}')

      if initial_image is not None:
        log.info(f'session_{session_id}_{batch_id}.initial_image          = {initial_image}')
        log.info(f'session_{session_id}_{batch_id}.image_denoise_strength = {image_denoise_strength}')
        print('initial_image =')
        display(get_image(initial_image))

      # print(f'image #{i*batch_size}-{i*batch_size+batch_size-1}')
      print(f'iteration {batch_id}')

      with torch.autocast('cuda'):
        if initial_image is None:
          images = self.text_to_image_pipeline(
            prompt              = [prompt]*batch_size,
            height              = size[0],
            width               = size[1],
            guidance_scale      = guidance_scale,
            num_inference_steps = num_inference_steps,
            generator           = self.torch_rng,
          ).images
        else:
          images = self.image_to_image_pipeline(
            init_image          = get_image(initial_image),
            strength            = image_denoise_strength,
            prompt              = [prompt]*batch_size,
            guidance_scale      = guidance_scale,
            num_inference_steps = num_inference_steps,
            generator           = self.torch_rng,
          ).images
        result = PromptResult(
          session_id             = session_id,
          batch_id               = batch_id,
          images                 = images,
          prompt                 = prompt,
          num_inference_steps    = num_inference_steps,
          guidance_scale         = guidance_scale,
          random_seed            = random_seed,
          initial_image          = initial_image,
          image_denoise_strength = image_denoise_strength,
        )
        yield result

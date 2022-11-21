from .prompt import SdmPromptContext
from .prompt import SdmPromptResult

import sys
import time
import torch
import PIL
import diffusers as ds
from loguru import logger as log
from torch import autocast

class SdmModelContext:
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
    gt = int(time.time())
    log.info(f'generate_{gt}()')
    log.info(f'generate_{gt}.batch_size = {batch_size}')
    log.info(f'generate_{gt}.iterations = {iterations}')

    image_cache = {}
    def get_image(path):
      if not path in image_cache:
        image_cache[path] = PIL.Image.open(path).convert('RGB')
      return image_cache[path]

    pinned_seed_value = None

    for i in range(iterations):
      with SdmPromptContext() as prompt_context:
        prompt_fn()

        seed_type, seed_value = prompt_context.random_seed
        if seed_type == 'pin':
          if i == 0:
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

      log.info(f'generate_{gt}_{i}()')
      log.info(f'generate_{gt}_{i}.prompt                 = {prompt}')
      log.info(f'generate_{gt}_{i}.prompt.len             = {len(prompt)}')
      log.info(f'generate_{gt}_{i}.prompt.hash            = {hash(prompt)}')
      log.info(f'generate_{gt}_{i}.size                   = {size}')
      log.info(f'generate_{gt}_{i}.random_seed            = {random_seed}')
      log.info(f'generate_{gt}_{i}.guidance_scale         = {guidance_scale}')
      log.info(f'generate_{gt}_{i}.num_inference_steps    = {num_inference_steps}')

      if initial_image is not None:
        log.info(f'generate_{gt}_{i}.initial_image          = {initial_image}')
        log.info(f'generate_{gt}_{i}.image_denoise_strength = {image_denoise_strength}')
        print('initial_image =')
        display(get_image(initial_image))

      # print(f'image #{i*batch_size}-{i*batch_size+batch_size-1}')
      print(f'iteration {i}')

      with autocast('cuda'):
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
        result = SdmPromptResult(
          created_time           = int(time.time()),
          images                 = images,
          prompt                 = prompt,
          num_inference_steps    = num_inference_steps,
          guidance_scale         = guidance_scale,
          random_seed            = random_seed,
          initial_image          = initial_image,
          image_denoise_strength = image_denoise_strength,
        )
        yield result

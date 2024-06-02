from typing import Optional

import PIL
import torch
import diffusers

class Playground:
  model_name: str
  model: diffusers.DiffusionPipeline
  rng: torch.Generator

  def __init__(
    self,
    cache_dir: Optional[str] = None,
    local_files_only: bool = False,
    use_gpu: bool = True,
  ):
    # self.model_name = 'stabilityai/stable-diffusion-xl-base-1.0'
    self.model_name = 'playgroundai/playground-v2.5-1024px-aesthetic'
    self.model = diffusers.StableDiffusionXLPipeline.from_pretrained(
      self.model_name,
      torch_dtype=torch.float16,
      use_safetensors=True,
      variant='fp16',
      cache_dir=cache_dir,
      local_files_only=local_files_only,
    )
    if use_gpu:
      self.model = self.model.to('cuda')
    self.model.enable_attention_slicing()
    self.model.enable_vae_slicing()

    print(f'model.device = {self.model.device}')
    self.rng = torch.Generator(self.model.device)

  def __call__(
    self,
    text: str | list[str],
    cotext: str | list[str] = '',
    xsize: int = 1024,
    ysize: int = 1024,
    num_inference_steps: int = 50,
    guidance_scale: float = 13.0,
    random_seed: int = 0,
    batch_size: int = 4,
  ) -> list[PIL.Image.Image]:
    self.rng.manual_seed(random_seed)
    if isinstance(text, str):
      text = [text]*batch_size
    if isinstance(cotext, str):
      cotext = [cotext]*batch_size
    assert len(text) == batch_size
    assert len(cotext) == batch_size
    target = self.model(
      prompt=text,
      negative_prompt=cotext,
      width=xsize,
      height=ysize,
      num_inference_steps=num_inference_steps,
      guidance_scale=guidance_scale,
      generator=self.rng,
    )
    images = target.images
    return images

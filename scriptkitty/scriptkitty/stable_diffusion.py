from typing import Optional

import PIL
import torch
import diffusers
import transformers

def t5_xxl_8bit():
  encoder = transformers.T5EncoderModel.from_pretrained(
    'stabilityai/stable-diffusion-3-medium-diffusers',
    subfolder='text_encoder_3',
    quantization_config=transformers.BitsAndBytesConfig(load_in_8bit=True),
  )
  return encoder

class Model:
  model_name: str
  model: diffusers.DiffusionPipeline
  rng: torch.Generator

  def __init__(
    self,
    cache_dir: Optional[str] = None,
    local_files_only: bool = False,
    use_gpu: bool = True,
  ):
    self.model_name = 'stabilityai/stable-diffusion-3-medium-diffusers'
    self.model = diffusers.StableDiffusion3Pipeline.from_pretrained(
      # 'stabilityai/stable-diffusion-3-medium-diffusers',
      self.model_name,
      torch_dtype=torch.float16,
      use_safetensors=True,
      text_encoder_3=t5_xxl_8bit(),
      device_map='balanced',
      # TODO: Apparently these are for the T5-XXL encoder, I suppose we can
      # simply remove them in order to use less memory.
      #text_encoder_3=None,
      #tokenizer_3=None,
      #variant='fp16',
      cache_dir=cache_dir,
      local_files_only=local_files_only,
    )
    if use_gpu:
      self.model = self.model.to('cuda')
      # TODO: not sure of compatibility between these options
      self.model.enable_attention_slicing()
      self.model.enable_vae_slicing()
    else:
      pass
      # self.model.enable_model_cpu_offload()

    # print(f'model.device = {self.model.device}')
    # self.rng = torch.Generator(self.model.device)
    self.rng = torch.Generator()

  def __call__(
    self,
    text: str | list[str],
    cotext: str | list[str] = '',
    xsize: int = 1024,
    ysize: int = 1024,
    num_inference_steps: int = 50,
    guidance_scale: float = 3.0,
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

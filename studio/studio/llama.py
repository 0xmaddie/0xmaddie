import torch
import transformers

class Llama:
  tokenizer: transformers.AutoTokenizer
  model: transformers.AutoModelForCausalLM
  system_prompt: str
  temperature: float
  max_new_tokens: int
  terminators: list
  purity: int
  quota: int

  def __init__(
    self,
    system_prompt: str = 'You are a helpful assistant.',
    temperature: float = 0.7,
    max_new_tokens: int = 4096,
    cache_dir=None,
    local_files_only=False,
    purity: int = 100,
    quota: int = 1000,
    tokenizer = None,
    model = None,
  ):
    model_name = 'meta-llama/Meta-Llama-3-8B-Instruct'
    self.tokenizer = tokenizer or transformers.AutoTokenizer.from_pretrained(
      model_name,
      cache_dir=cache_dir,
      local_files_only=local_files_only,
    )
    self.model = model or transformers.AutoModelForCausalLM.from_pretrained(
      model_name,
      device_map='auto',
      # TODO: There was some FUD about Llama 3 quantization being a
      # problem, is there any truth to this?
      load_in_8bit=True,
      cache_dir=cache_dir,
      local_files_only=local_files_only,
    )
    self.terminators = [
      self.tokenizer.eos_token_id,
      self.tokenizer.convert_tokens_to_ids('<|eot_id|>')
    ]
    self.system_prompt  = system_prompt
    self.temperature    = temperature
    self.max_new_tokens = max_new_tokens
    self.purity         = purity
    self.quota          = quota

  def __apply_chat_template(self, state):
    prompt = [{ 'role': 'system', 'content': self.system_prompt }]
    for index, content in enumerate(state):
      if index%2 == 0:
        role = 'user'
      else:
        role = 'assistant'
      prompt.append({ 'role': role, 'content': content })
    input_ids = self.tokenizer.apply_chat_template(
      prompt,
      #tokenize=True,
      add_generation_prompt=True,
      return_tensors='pt',
    ).to(self.model.device)

    return input_ids

  def get(self, state):
    source_ids = self.__apply_chat_template(state)
    targets    = self.model.generate(
      source_ids,
      max_new_tokens=self.max_new_tokens,
      do_sample=True,
      temperature=self.temperature,
      eos_token_id=self.terminators,
    )
    target_ids = targets[0][source_ids.shape[-1]:]
    target     = self.tokenizer.decode(target_ids, skip_special_tokens=True)
    return target

  def reduce(self, input, map, reduce):
    quota   = self.quota
    samples = []
    while quota > 0 and len(samples) < self.purity:
      quota -= 1
      samples.clear()
      try:
        value = map(self.get(input))
        samples.append(value)
      except ValueError:
        pass
    if len(samples) < self.purity and quota == 0:
      raise ValueError(f'Llama.reduce: quota consumed')
    output = reduce(samples)
    return output

import numpy as np
import scipy as sp
import functools

from typing import Callable
from typing import List

_weight_stack = []

class WeightContext:
  buf: np.ndarray
  idx: int = 0

  def __init__(self, buf: np.ndarray):
    self.buf = buf

  def __enter__(self):
    _weight_stack.append(self)
    return self

  def __exit__(self, kind, err, traceback):
    _weight_stack.pop()
    return False

  def use_weights(self, shape) -> np.ndarray:
    req = functools.reduce(lambda s, x: s*x, shape)
    if self.idx+req > len(self.buf):
      num = f'{self.idx+req}/{len(self.buf)}'
      raise ValueError(f'weights exhausted: {num}')
    weights = self.buf[self.idx:self.idx+req]
    weights = weights.reshape(shape)
    self.idx = self.idx+req
    return weights

def use_weights(shape) -> np.ndarray:
  global _weight_stack
  ctx = _weight_stack[-1]
  return ctx.use_weights(shape)

def random_weights(size: int) -> WeightContext:
  rng = np.random.default_rng()
  buf = rng.standard_normal(size)
  return WeightContext(buf)

def relu(src: np.ndarray) -> np.ndarray:
  dst = np.maximum(src, 0)
  return dst

def standardize(src: np.ndarray) -> np.ndarray:
  mean = np.mean(src,axis=-1,keepdims=True)
  var = np.mean(
    np.square(src),
    axis=-1,
    keepdims=True,
  ) - np.square(mean)
  stddev = np.sqrt(var)
  dst = (src-mean)/(stddev+1e-5)
  return dst

def layer_norm(
  src: np.ndarray,
) -> np.ndarray:
  _, seq, dim = src.shape
  gain = use_weights((seq, dim))
  bias = use_weights((seq, dim))
  return gain*standardize(src)+bias

class Fwd:
  dhidden: int

  def __init__(self, dhidden: int):
    self.dhidden = dhidden

  def __call__(self, src: np.ndarray) -> np.ndarray:
    _, _, din = src.shape

    w0 = use_weights((din, self.dhidden))
    w1 = use_weights((self.dhidden, din))
    b0 = use_weights((self.dhidden,))
    b1 = use_weights((din,))

    return relu(src@w0+b0)@w1+b1

class Mhsa:
  heads: int

  def __init__(self, heads: int):
    self.heads = heads

  def __call__(self, src: np.ndarray) -> np.ndarray:
    batch, seq, din = src.shape
    dhidden = din//self.heads

    Q = use_weights((self.heads, din, dhidden))
    K = use_weights((self.heads, din, dhidden))
    V = use_weights((self.heads, din, dhidden))
    O = use_weights((din, din))

    src   = src.reshape(batch, 1, seq, din)

    query = src@Q # [batch, heads, seq, dhidden]
    key   = src@K # [batch, heads, seq, dhidden]
    value = src@V # [batch, heads, seq, dhidden]

    key = key.transpose(0, 1, 3, 2) # [batch, heads, dhidden, seq]

    energy = query@key # [batch, heads, seq, seq]
    energy = energy/np.sqrt(dhidden)
    energy = sp.special.softmax(energy)

    target = energy@value                      # [batch, heads, seq, dhidden]
    target = target.transpose(0, 2, 1, 3)      # [batch, seq, heads, dhidden]
    target = target.reshape((batch, seq, din)) # [batch, seq, din]
    
    target = target@O

    return target

class Mixer:
  din: int
  dout: int
  dhidden: int
  depth: int
  mix: Callable[[np.ndarray], np.ndarray]
  map: Callable[[np.ndarray], np.ndarray]

  def __init__(
    self,
    din: int,
    dout: int,
    dhidden: int,
    mix: Callable[[np.ndarray], np.ndarray],
    map: Callable[[np.ndarray], np.ndarray],
    depth: int = 2,
  ):
    self.din = din
    self.dout = dout
    self.dhidden = dhidden
    self.mix = mix
    self.map = map
    self.depth = depth

  def __call__(self, state: np.ndarray) -> np.ndarray:
    # Train an embedding to the model dimension end-to-end.
    encode = use_weights((self.din, self.dhidden))
    decode = use_weights((self.dhidden, self.dout))

    state = state@encode

    for _ in range(self.depth):
      state = state+self.mix(state)
      state = layer_norm(state)
      state = state+self.map(state)
      state = layer_norm(state)

    state = sp.special.softmax(state@decode, axis=-1)

    return state
  
class Dictionary:
  tokens: List[str]
  one_hot: np.ndarray

  def __init__(self, tokens: List[str]):
    self.tokens  = tokens
    self.one_hot = np.eye(len(self.tokens))

  def encode(self, src: str) -> np.ndarray:
    tokens  = src.split(' ')
    indices = [self.tokens.index(tx) for tx in tokens]
    tensor  = self.one_hot[indices]
    return tensor

  def decode(self, src: np.ndarray) -> str:
    rng    = np.random.default_rng()
    tokens = [rng.choice(self.tokens, p=p) for p in src]
    dst    = ' '.join(tokens)
    return dst

class Loss:
  tokens: Dictionary
  corpus: List[str]
  model: Callable[[np.ndarray], np.ndarray]

  def __call__(self, weights: np.ndarray) -> float:
    return 0.0

if __name__ == '__main__':
  dx = Dictionary('a b c d _'.split(' '))
  model = Mixer(
    din=5,
    dout=5,
    dhidden=125,
    mix=Mhsa(heads=5),
    map=Fwd(dhidden=125*4),
    depth=2,
  )
  with random_weights(2**20) as ctx:
    source_string = ['a a b b c c d d']
    source_tensor = np.array([dx.encode(src) for src in source_string])
    target_tensor = model(source_tensor)
    target_string = [dx.decode(dst) for dst in target_tensor]
    print(f'{source_string} -> {target_string}')
    print(f'source_tensor.shape = {source_tensor.shape}')
    print(f'target_tensor.shape = {target_tensor.shape}')

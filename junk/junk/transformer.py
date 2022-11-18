from functools import reduce
import numpy as np
from scipy.special import softmax

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
    req = reduce(lambda s, x: s*x, shape)
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
  # dim: int,
) -> np.ndarray:
  _, dim = src.shape
  gain = use_weights((dim,))
  bias = use_weights((dim,))
  return gain*standardize(src)+bias

def mlp(
  x: np.ndarray,
  # dim: int = 512,
) -> np.ndarray:
  _, dim = x.shape
  W = use_weights((dim, dim))
  b = use_weights((dim,))
  return relu(x@W+b)

def mhsa(
  x: np.ndarray,
  # dim: int   = 512,
  # seq: int   = 128,
  heads: int = 8,
) -> np.ndarray:
  seq, dim = x.shape

  Q      = use_weights((heads, dim, dim//heads))
  K      = use_weights((heads, dim, dim//heads))
  V      = use_weights((heads, dim, dim//heads))
  O      = use_weights((dim, dim))
  query  = x@Q
  key    = x@K
  value  = x@V
  energy = query@key.transpose(0, 2, 1)
  energy = energy/np.sqrt(dim//heads)
  scale  = softmax(energy)
  target = scale@value
  target = target.transpose(1, 0, 2)
  target = target.reshape((seq, dim))
  target = target@O

  return target

class Transformer:
  dinput: int
  doutput: int
  dmodel: int
  dfwd: int
  depth: int
  heads: int

  def __init__(
    self,
    dinput: int = 16,
    doutput: int = 16,
    dmodel: int = 64,
    dfwd: int = 256,
    depth: int = 2,
    heads: int = 4,
  ):
    self.dinput  = dinput
    self.doutput = doutput
    self.dmodel  = dmodel
    self.dfwd    = dfwd
    self.depth   = depth
    self.heads   = heads

  def __call__(self, state: np.ndarray) -> np.ndarray:
    # Train an embedding to the model dimension end-to-end.
    encode = use_weights((self.dinput, self.dmodel))
    decode = use_weights((self.dmodel, self.doutput))

    state = state@encode

    for _ in range(self.depth):
      state = state+mhsa(state, heads=self.heads)
      state = layer_norm(state)
      # todo: use dfwd here
      # attention is all you need used a fwd layer like
      # relu(xw+b)u+c
      # i.e. two linear maps, going bigger to dfwd then back to dmodel
      state = state+mlp(state)
      state = layer_norm(state)

    state = softmax(state@decode)

    return state

class Dictionary:
  tokens: list[str]
  one_hot: np.ndarray

  def __init__(self, tokens: str):
    self.tokens  = tokens.split(' ')
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

if __name__ == '__main__':
  dx    = Dictionary('a b c d _')
  model = Transformer(depth=2, heads=4)
  with random_weights(2**16) as ctx:
    source = 'a a b b c c d d'
    target = dx.decode(model(dx.encode(source)))
    print(f'{source} -> {target}')

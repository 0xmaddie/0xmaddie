from functools import reduce
import numpy as np
from scipy.special import softmax

_weight_context = None

class WeightContext:
  buf: np.ndarray
  idx: int = 0

  def __init__(self, buf: int | np.ndarray):
    if isinstance(buf, int):
      rng      = np.random.default_rng()
      self.buf = rng.standard_normal(buf)
    else:
      self.buf = buf

  def bind(self):
    global _weight_context
    assert _weight_context is None
    _weight_context = self

  def unbind(self):
    global _weight_context
    assert _weight_context == self
    _weight_context = None

  def use_weights(self, shape) -> np.ndarray:
    req = reduce(lambda s, x: s*x, shape)
    if self.idx+req > len(self.buf):
      num = f'{self.idx+req}/{len(self.buf)}'
      raise ValueError(f'weights exhausted: {num}')
    weights  = self.buf[self.idx:self.idx+req]
    weights  = weights.reshape(shape)
    self.idx = self.idx+req
    return weights

def use_weights(shape) -> np.ndarray:
  global _weight_context
  assert _weight_context
  return _weight_context.use_weights(shape)

def relu(src: np.ndarray) -> np.ndarray:
  dst = np.maximum(src, 0)
  return dst

def norm(src: np.ndarray) -> np.ndarray:
  mean   = np.mean(src,axis=-1,keepdims=True)
  var    = np.mean(
    np.square(src),
    axis=-1,
    keepdims=True,
  ) - np.square(mean)
  stddev = np.sqrt(var)
  dst    = (src-mean)/(stddev+1e-5)
  return dst

def layer_norm(
  src: np.ndarray,
  dim: int,
) -> np.ndarray:
  gain = use_weights((dim,))
  bias = use_weights((dim,))
  return gain*norm(src)+bias

def ffwd(
  x: np.ndarray,
  dim: int = 512,
) -> np.ndarray:
  W = use_weights((dim, dim))
  b = use_weights((dim,))
  return relu(x@W+b)

def attn(
  x: np.ndarray,
  dim: int   = 512,
  seq: int   = 128,
  heads: int = 8,
) -> np.ndarray:
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

def transformer(
  src: np.ndarray,
  depth: int = 4,
  heads: int = 8,
  dim: int = 512,
  seq: int = 64,
) -> np.ndarray:
  for _ in range(depth):
    print(f'x={src}')
    src = src+attn(src, heads=heads, dim=dim, seq=seq)
    print(f'x={src}')
    src = layer_norm(src, dim=dim)
    print(f'x={src}')
    src = src+ffwd(src, dim=dim)
    print(f'x={src}')
    src = layer_norm(src, dim=dim)
    print(f'x={src}')
  return src

if __name__ == '__main__':
  ctx = WeightContext(2**16)
  dim = 4
  seq = 4
  rng = np.random.default_rng()
  src = rng.standard_normal((seq, dim))
  ctx.bind()
  dst = transformer(
    src,
    depth=2,
    heads=4,
    dim=dim,
    seq=seq,
  )
  ctx.unbind()

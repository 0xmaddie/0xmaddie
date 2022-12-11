from typing import Tuple
from typing import Optional
from typing import Callable
from typing import Generator

import dataclasses

import functools as fn
import numpy as np
import scipy as sp

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

class Command:
  pass

@dataclasses.dataclass(frozen=True)
class UseWeights(Command):
  shape: Tuple[int, ...]

Layer = Callable[
  [np.ndarray],
  Generator[Command, np.ndarray, np.ndarray],
]

def layer_norm(
  src: np.ndarray,
) -> Generator[Command, np.ndarray, np.ndarray]:
  _, seq, dim = src.shape
  gain = yield UseWeights((seq, dim))
  bias = yield UseWeights((seq, dim))
  return gain*standardize(src)+bias

@dataclasses.dataclass(frozen=True)
class Feedforward:
  dhidden: int

  def __call__(
    self,
    src: np.ndarray,
  ) -> Generator[Command, np.ndarray, np.ndarray]:
    _batch, _seq, din = src.shape

    w0 = yield UseWeights((din, self.dhidden))
    w1 = yield UseWeights((self.dhidden, din))
    b0 = yield UseWeights((self.dhidden,))
    b1 = yield UseWeights((din,))

    return relu(src@w0+b0)@w1+b1

class Mhsa:
  pass

class Mixer:
  mix: Layer
  map: Layer
  depth: int
  dhidden: int

  def __init__(
    self,
    mix: Layer,
    map: Layer,
    depth: int,
    dhidden: int,
  ):
    self.mix = mix
    self.map = map
    self.depth = depth
    self.dhidden = dhidden

  def __call__(
    self,
    value: np.ndarray,
  ) -> Generator[Command, np.ndarray, np.ndarray]:
    _batch, _seq, din = value.shape

    encode = yield UseWeights((din, self.dhidden))
    decode = yield UseWeights((self.dhidden, din))

    value = value@encode
    
    for _ in range(self.depth):
      value = value+(yield from self.mix(value))
      value = yield from layer_norm(value)
      value = value+(yield from self.map(value))
      value = yield from layer_norm(value)

    value = value@decode
    value = sp.special.softmax(value, axis=-1)

    return value

@dataclasses.dataclass(frozen=True)
class Model:
  body: Layer
  weights: np.ndarray

  def __call__(self, src: np.ndarray) -> np.ndarray:
    idx = 0
    net = self.body(src)
    try:
      cmd = next(net)
      while True:
        if isinstance(cmd, UseWeights):
          size = fn.reduce(lambda s,x: s*x, cmd.shape)
          if idx+size > len(self.weights):
            raise ValueError(f'weights exhausted: {idx+size}')
          weights = self.weights[idx:idx+size]
          weights = weights.reshape(cmd.shape)
          idx = idx+size
          cmd = net.send(weights)
        else:
          raise ValueError(f'unknown command: {cmd}')
    except StopIteration as stop:
      result = stop.value
      return result

def gradient_descent(
  init: np.ndarray,
  loss: Callable[[np.ndarray], float],
  steps: int = 1000,
  learning_rate: float = 0.1,
) -> np.ndarray:
  state = init
  for i in range(steps):
    gradient = jax.grad(loss)(state)
    state = state - learning_rate*gradient
  return state

def select_batch(
  corpus: list[str],
  dictionary: Callable[[str], np.ndarray],
  batch_size: int,
) -> np.ndarray:
  pass

def cross_entropy(
  lhs: np.ndarray,
  rhs: np.ndarray,
) -> float:
  return np.mean(-np.sum(lhs*np.log(rhs), axis=(-1,-2)))

if __name__ == '__main__':
  pass

import sys
import time
import math
import dataclasses
import functools as fn
import numpy as np
import cairo
import opensimplex

from typing import Tuple
from typing import List
from typing import Callable
from typing import Generator

_weight_context = []
      
class WeightContext:
  weights: np.ndarray
  stack: List[int]
  index: int = 0
  
  def __init__(self, weights: np.ndarray | int | float):
    if isinstance(weights, np.ndarray):
      self.weights = weights
    else:
      rng = np.random.default_rng()
      self.weights = rng.standard_normal(int(weights))
    self.stack = []

  def __enter__(self):
    global _weight_context
    _weight_context.append(self)
    return self

  def __exit__(self, err_type, err_value, traceback):
    global _weight_context
    assert _weight_context[-1] is self
    _weight_context.pop()

  def save(self):
    self.stack.append(self.index)

  def restore(self):
    self.index = self.stack.pop()
    
  def use_weights(self, shape: Tuple[int, ...]) -> np.ndarray:
    num_param = fn.reduce(lambda s, x: s*x, shape)
    if self.index+num_param > len(self.weights):
      raise ValueError(f'weights exhausted')
    weights = self.weights[self.index:self.index+num_param]
    weights = weights.reshape(shape)
    self.index += num_param
    return weights

def use_weights(shape: Tuple[int, ...]) -> np.ndarray:
  global _weight_context
  ctx = _weight_context[-1]
  return ctx.use_weights(shape)

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

def layer_norm(state: np.ndarray) -> np.ndarray:
  dim = state.shape[-1]
  gain = use_weights((dim,))
  bias = use_weights((dim,))
  return gain*standardize(state)+bias

def resnet(
  state: np.ndarray,
  depth: int = 2,
  hidden_factor: int = 4,
) -> np.ndarray:
  dim = state.shape[-1]
  for _ in range(depth):
    w0 = use_weights((dim, hidden_factor*dim))
    b0 = use_weights((hidden_factor*dim,))
    w1 = use_weights((hidden_factor*dim, dim))
    b1 = use_weights((dim,))
    state = state+relu(state@w0+b0)@w1+b1
    state = layer_norm(state)
  return state

def pendulum(time: float, grade: int = 4) -> np.ndarray:
  state = np.array([0.0, 0.0])
  weights = use_weights((grade, 4))
  for row in weights:
    xfreq, xphase, yfreq, yphase = row
    residual = np.array([
      np.cos(time*xfreq*2*math.pi+xphase),
      np.sin(time*yfreq*2*math.pi+yphase),
    ])
    state += residual*(1/grade)
  return state

def draw_pendulum_example():
  WIDTH = 1024
  HEIGHT = 1024
  surface = cairo.ImageSurface(
    cairo.FORMAT_ARGB32,
    WIDTH,
    HEIGHT,
  )
  ctx = cairo.Context(surface)

  # Enter normalized device coordinates.
  ctx.save()
  ctx.translate(WIDTH/2, HEIGHT/2)
  ctx.scale(WIDTH/2, HEIGHT/2)

  # Draw a solid color background.
  ctx.set_source_rgb(0.0, 0.0, 0.0)
  ctx.paint()

  window = 1.25
  iterations = 4096
  with WeightContext(1e4) as weights:
    for j in range(0, 4):
      for i in range(0, iterations):
        residual = (-window/2)+i*((1/iterations)*window)
        weights.save()
        x, y = pendulum(residual)
        weights.restore()
        radius = 2/128
        ctx.arc(x, y, radius, 0, 2*math.pi)
        # super pink
        ctx.set_source_rgb(0.839, 0.360, 0.678)
        ctx.fill()
      if j%2 == 0:
        ctx.scale(-1, 1)
      else:
        ctx.scale(1, -1)

  # Exit normalized device coordinates.
  ctx.restore()

  surface.write_to_png(f'cairo_template_{int(time.time())}.png')

if __name__ == '__main__':
  draw_pendulum_example()

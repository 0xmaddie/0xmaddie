import numpy as np
import opensimplex

# todo: this is not as general as it could be, since i'm not using ndarrays

def random() -> float:
  rng = np.random.default_rng()
  return rng.random()

def normal(mean: float = 0, stddev: float = 1) -> float:
  rng = np.random.default_rng()
  return rng.normal(loc=mean, scale=stddev)

def coin(odds: float) -> float:
  rng = np.random.default_rng()
  return rng.random() < odds

def noise(x, y, z=None, w=None):
  if z is None and w is None:
    return opensimplex.noise2(x, y)
  if z is not None and w is None:
    return opensimplex.noise3(x, y, z)
  assert z is not None and w is not None
  return opensimplex.noise4(x, y, z, w)

def choice(xs, p=None):
  rng = np.random.default_rng()
  return rng.choice(xs, p=p)

def permute(xs):
  rng = np.random.default_rng()
  return rng.permutation(xs)

def pick(xs, p):
  rng = np.random.default_rng()
  n = rng.choice(range(1, len(p)+1), p=p)
  return permute(xs)[:n]

def maybe(fx, p):
  if coin(p):
    return fx
  return ''

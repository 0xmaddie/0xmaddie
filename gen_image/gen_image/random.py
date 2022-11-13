import numpy
import opensimplex

def rand():
  rng = numpy.random.default_rng()
  return rng.random()

def coin(odds):
  rng = numpy.random.default_rng()
  return rng.random() < odds

def noise(x, y, z=None, w=None):
  if z is None and w is None:
    return opensimplex.noise2(x, y)
  if z is not None and w is None:
    return opensimplex.noise3(x, y, z)
  assert z is not None and w is not None
  return opensimplex.noise4(x, y, z, w)

def choice(xs, p=None):
  rng = numpy.random.default_rng()
  return rng.choice(xs, p=p)

def shuffle(xs):
  rng = numpy.random.default_rng()
  return rng.permutation(xs)

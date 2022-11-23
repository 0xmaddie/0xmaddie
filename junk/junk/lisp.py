class Error(Exception):
  pass

class Object:
  pass

class Symbol(Object):
  pass

class Keyword(Object):
  pass

class Number(Object):
  pass

class Tensor(Object):
  pass

class String(Object):
  pass

class Nil(Object):
  pass

class Pair(Object):
  pass

class Array(Object):
  pass

class Map(Object):
  pass

class Environment(Object):
  pass

class Procedure(Object):
  pass

class Wrap(Procedure):
  pass

class Vau(Procedure):
  pass

class Reader:
  def encode(self, obj: Object) -> str:
    pass

  def decode(self, src: str) -> Object:
    pass

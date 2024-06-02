from typing import Optional
from typing import Callable
import dataclasses

class Error(Exception):
  message: str
  value: Optional['Value']
  environment: Optional['Environment']

  def __init__(self, message, value=None, environment=None):
    self.message     = message
    self.value      = value
    self.environment = environment

  def __str__(self):
    return f'{self.message}'

def error(message):
  return Error(message)

def atomic_error(proc, args, env, err):
  message = f'''
Lisp produced an error while applying the atomic procedure

```
{proc.advice}
```

to the argument list

```
{args}
```

{err}
'''.strip()
  return error(message)

def abstract_error(proc, args, env, err):
  message = f'''
Lisp produced an error while applying the abstract procedure

```
(vau {proc.head} {proc.dynamic}
  {proc.body})
```

to the argument list

```
{args}
```

{err}
'''.strip()
  return error(message)

class Value:
  @property
  def is_nil(self):
    return False

  @property
  def is_pair(self):
    return False

  @property
  def is_list(self):
    return False

  @property
  def is_symbol(self):
    return False

  @property
  def is_constant(self):
    return False

  @property
  def is_variable(self):
    return False

  @property
  def is_boolean(self):
    return False

  @property
  def is_number(self):
    return False

  @property
  def is_string(self):
    return False

  @property
  def is_keyword(self):
    return False

  @property
  def is_environment(self):
    return False

  @property
  def is_procedure(self):
    return False

  @property
  def is_atomic(self):
    return False

  @property
  def is_abstract(self):
    return False

  @property
  def is_wrap(self):
    return False

  def assert_nil(self):
    if not self.is_nil:
      message = f'Expected nil, but got {self}.'
      raise error(message)

  def assert_pair(self):
    if not self.is_nil:
      message = f'Expected a pair, but got {self}.'
      raise error(message)

  def assert_list(self):
    if not self.is_list:
      message = f'Expected a list, but got {self}.'
      raise error(message)

  @property
  def to_constant(self):
    if not self.is_constant:
      message = f'Expected a constant, but got {self}.'
      raise error(message)
    return self.name

  @property
  def to_variable(self):
    if not self.is_variable:
      message = f'Expected a variable, but got {self}.'
      raise error(message)
    return self.name

  def assert_symbol(self):
    if not self.is_symbol:
      message = f'Expected a symbol:, but got {self}.'
      raise error(message)

  def assert_constant(self):
    if not self.is_constant:
      message = f'Expected a constant:, but got {self}.'
      raise error(message)

  def assert_variable(self):
    if not self.is_variable:
      message = f'Expected a variable, but got {self}.'
      raise error(message)

  @property
  def to_boolean(self):
    if not self.is_boolean:
      message = f'Expected a boolean, but got {self}.'
      raise error(message)
    return self.value

  @property
  def to_number(self):
    if not self.is_number:
      message = f'Expected a number, but got {self}.'
      raise error(message)
    return self.value

  @property
  def to_string(self):
    if not self.is_string:
      message = f'Expected a string, but got {self}.'
      raise error(message)
    return self.value

  @property
  def to_keyword(self):
    if not self.is_keyword:
      message = f'Expected a keyword, but got {self}.'
      raise error(message)
    return self.value

  def assert_environment(self):
    if not self.is_environment:
      message = f'Expected an environment, but got {self}.'
      raise error(message)

  def assert_procedure(self):
    if not self.is_procedure:
      message = f'Expected a procedure, but got {self}.'
      raise error(message)

  @property
  def to_wrap(self):
    if not self.is_wrap:
      message = f'Expected a wrapped procedure, but got {self}.'
      raise error(message)
    return self.body

  @property
  def fst(self):
    message = f'Expected a pair, but got {self}.'
    raise error(message)

  @property
  def snd(self):
    message = f'Expected a pair, but got {self}.'
    raise error(message)

  @property
  def body(self):
    message = f'The value {self} does not have an attribute named `body`.'
    raise error(message)

  @property
  def name(self):
    message = f'The value {self} does not have an attribute named `name`.'
    raise error(message)

  @property
  def value(self):
    message = f'The value {self} does not have an attribute named `value`.'
    raise error(message)

  @property
  def next(self):
    message = f'The value {self} does not have an attribute named `next`.'
    raise error(message)

  @property
  def head(self):
    message = f'The value {self} does not have an attribute named `head`.'
    raise error(message)

  @property
  def dynamic(self):
    message = f'The value {self} does not have an attribute named `dynamic`.'
    raise error(message)

  @property
  def lexical(self):
    message = f'The value {self} does not have an attribute named `lexical`.'
    raise error(message)

  @property
  def length(self):
    message = f'The value {self} does not have an attribute named `length`.'
    raise error(message)

  def __contains__(self, key):
    message = f'Expected an environment, but got {self}.'
    raise error(message)

  def __getitem__(self, key):
    message = f'Expected an environment, but got {self}.'
    raise error(message)

  def __setitem__(self, key, value):
    message = f'Expected an environment, but got {self}.'
    raise error(message)

  def __str__(self):
    return _show(self)

@dataclasses.dataclass(frozen=True)
class Nil(Value):
  @property
  def is_nil(self):
    return True

  @property
  def is_list(self):
    return True

  @property
  def length(self):
    return 0

  def __contains__(self, key):
    return False

@dataclasses.dataclass(frozen=True)
class Pair(Value):
  __fst: Value
  __snd: Value

  @property
  def is_pair(self):
    return True

  @property
  def is_list(self):
    return self.__snd.is_list

  @property
  def length(self):
    return 1+self.__snd.length

  @property
  def fst(self):
    return self.__fst

  @property
  def snd(self):
    return self.__snd

  def __contains__(self, value):
    self.assert_list()
    xs = self
    while not xs.is_nil:
      if value == xs.fst:
        return True
      xs = xs.snd
    return False

  def __getitem__(self, index):
    self.assert_list()
    state = index
    xs = self
    while not xs.is_nil:
      if state == 0:
        return xs.fst
      state = state-1
      xs    = xs.snd
    message = f'List index out of bounds: {index}.'
    raise error(message)

  def __setitem__(self, index, value):
    message = f'Lists are immutable.'
    raise error(message)

@dataclasses.dataclass(frozen=True)
class Constant(Value):
  __name: str

  @property
  def is_symbol(self):
    return True

  @property
  def is_constant(self):
    return True

  @property
  def name(self):
    return self.__name

@dataclasses.dataclass(frozen=True)
class Variable(Value):
  __name: str

  @property
  def is_symbol(self):
    return True

  @property
  def is_variable(self):
    return True

  @property
  def name(self):
    return self.__name

@dataclasses.dataclass(frozen=True)
class Boolean(Value):
  __value: bool

  @property
  def is_boolean(self):
    return True

  @property
  def value(self):
    return self.__value

@dataclasses.dataclass(frozen=True)
class Number(Value):
  __value: float

  @property
  def is_number(self):
    return True

  @property
  def value(self):
    return self.__value

@dataclasses.dataclass(frozen=True)
class String(Value):
  __value: str

  @property
  def is_string(self):
    return True

  @property
  def value(self):
    #string = self.__value.replace('"', '\\"')
    #return string
    string = self.__value
    return f'"{string}"'

@dataclasses.dataclass(frozen=True)
class Keyword(Value):
  __value: str

  @property
  def is_keyword(self):
    return True

  @property
  def value(Self):
    return self.__value

class Environment(Value):
  __body: dict[str, Value]
  __next: Optional['Environment']

  def __init__(self, body=None, next=None):
    if body is None:
      self.__body = {}
    else:
      self.__body = body
    self.__next = next

  @property
  def is_environment(self):
    return True

  @property
  def body(self):
    return self.__body

  @property
  def next(self):
    return self.__next

  def __contains__(self, key):
    match key:
      case Constant(name):
        return name in _constants
      case Variable(name):
        env = self
        while env is not None:
          if name in env.body:
            return True
          env = env.next
        return False
      case str(name):
        if name[0].isupper():
          name = constant(name)
        else:
          name = variable(name)
        return name in self
      case _:
        return False

  def __getitem__(self, key):
    match key:
      case Constant(name):
        if name in _constants:
          return _constants[name]
        msg = f'The symbol {name} is undefined.'
        raise error(msg)
      case Variable(name):
        env = self
        while env is not None:
          if name in env.body:
            return env.body[name]
          env = env.next
        msg = f'The symbol {name} is undefined.'
        raise error(msg)
      case str(name):
        if name[0].isupper():
          name = constant(name)
        else:
          name = variable(name)
        return self[name]
      case _:
        msg = f'Cannot retrieve the value bound to `{key}`'
        raise error(msg)

  def __setitem__(self, key, value):
    match key:
      case Nil():
        match value:
          case Nil():
            pass
          case _:
            msg = f'Cannot bind nil to the non-nil value {value}'
            raise error(msg)
      case Constant(name):
        msg = f'The symbol {name} is a constant and cannot be redefined.'
        raise error(msg)
      case Variable(name):
        if name in self.body:
          msg = f'The symbol {name} is already bound to a value and cannot be redefined.'
          raise error(msg)
        self.body[name] = value
      case Keyword(name):
        match name:
          case ':none':
            pass
          case _:
            msg = f'Unexpected keyword during variable binding: {key}'
            raise error(msg)
      case str(name):
        if name[0].isupper():
          name = constant(name)
        elif name[0] == ':':
          name = keyword(name)
        else:
          name = variable(name)
        self[name] = value
      case _:
        msg = f'Cannot bind a value to `{key}`'
        raise error(msg)

@dataclasses.dataclass(frozen=True, eq=False)
class Atomic(Value):
  @property
  def is_procedure(self):
    return True

  @property
  def is_atomic(self):
    return True

@dataclasses.dataclass(frozen=True, eq=False)
class Abstract(Value):
  __head: Value
  __body: Value
  __dynamic: Value
  __lexical: Value

  @property
  def is_procedure(self):
    return True

  @property
  def is_abstract(self):
    return True

  @property
  def head(self):
    return self.__head

  @property
  def body(self):
    return self.__body

  @property
  def dynamic(self):
    return self.__dynamic

  @property
  def lexical(self):
    return self.__lexical

@dataclasses.dataclass(frozen=True, eq=False)
class Wrap(Value):
  __body: Value

  @property
  def is_procedure(self):
    return True

  @property
  def is_wrap(self):
    return True

  @property
  def body(self):
    return self.__body

def nil():
  return Nil()

def pair(fst, snd):
  return Pair(fst, snd)

def list(*args):
  return from_list(args)

def constant(name):
  assert isinstance(name, str)
  return Constant(name)

def variable(name):
  assert isinstance(name, str)
  return Variable(name)

def keyword(name):
  assert isinstance(name, str)
  return Keyword(name)

def boolean(value):
  assert isinstance(value, bool)
  return Boolean(value)

def number(value):
  return Number(value)

def string(value):
  assert isinstance(value, str)
  return String(value)

def environment(body=None, next=None):
  if body is not None and not isinstance(body, dict):
    raise error(f'Cannot construct an environment with the body {body}')
  if next is not None:
    next.assert_environment()
  return Environment(body, next)

def atomic(body):
  return Atomic(body)

def abstract(head, body, dynamic, lexical):
  # head.assert_list()
  body.assert_list()
  # dynamic.assert_variable()
  lexical.assert_environment()
  return Abstract(head, body, dynamic, lexical)

def wrap(body):
  body.assert_procedure()
  return Wrap(body)

def from_list(xs):
  state = nil()
  for child in reversed(xs):
    state = pair(child, state)
  return state

def from_dict(xs):
  buf = []
  for key, value in sorted(xs.items()):
    buf.append(pair(string(key), value))
  return from_list(buf)

def is_lparen(source, index):
  return source[index] == '('

def is_rparen(source, index):
  return source[index] == ')'

def is_begin_string(source, index):
  return source[index] == '"'

def is_end_string(source, index):
  if index == 0:
    return source[index] == '"'
  return source[index] == '"' and source[index-1] != '\\'

def is_whitespace(source, index):
  return source[index] in [' ', '\t', '\r', '\n']

def is_separator(source, index):
  if is_lparen(source, index):
    return True
  if is_rparen(source, index):
    return True
  if is_begin_string(source, index):
    return True
  if is_whitespace(source, index):
    return True
  return False

def is_unreadable(symbol):
  return symbol.startswith('#<')

def is_constant(symbol):
  return len(symbol) > 0 and symbol[0].isupper()

def is_keyword(symbol):
  return len(symbol) > 0 and symbol[0] == ':'

def read(source: str):
  stack = []
  build = []
  index = 0

  def seek_while(fn):
    nonlocal source
    nonlocal index
    while index < len(source) and fn(source, index):
      index += 1

  def seek_until(fn):
    nonlocal source
    nonlocal index
    while index < len(source) and not fn(source, index):
      index += 1

  while index < len(source):
    if is_lparen(source, index):
      stack.append(build)
      build = []
      index += 1
    elif is_rparen(source, index):
      if len(stack) == 0:
        msg = f'Unbalanced parentheses within source code:\n{source}'
        raise error(msg)
      xs = from_list(build)
      build = stack.pop()
      build.append(xs)
      index += 1
    elif is_begin_string(source, index):
      index += 1
      start  = index
      seek_until(is_end_string)
      body = source[start:index]
      build.append(string(body))
      index += 1
    elif is_whitespace(source, index):
      seek_while(is_whitespace)
    else:
      start = index
      seek_until(is_separator)
      body = source[start:index]
      if is_unreadable(body):
        msg = f'Unreadable symbol {body} within source code:\n{source}'
        raise error(msg)
      try:
        value = float(body)
        build.append(number(value))
      except ValueError:
        if is_constant(body):
          build.append(constant(body))
        elif is_keyword(body):
          build.append(keyword(body))
        else:
          build.append(variable(body))
  return build

def _show(obj):
  match obj:
    case Nil():
      return '()'
    case Pair(fst, snd):
      if obj.is_list:
        buf = []
        while not obj.is_nil:
          hidden = _show(obj.fst)
          buf.append(hidden)
          obj = obj.snd
        body = ' '.join(buf)
        return f'({body})'
      else:
        fst_ = _show(fst)
        snd_ = _show(snd)
        return f'(Pair {fst_} {snd_})'
    case Constant(name):
      return name
    case Variable(name):
      return name
    case Boolean(value):
      return str(value)
    case Number(value):
      return str(value)
    case String(_):
      return obj.value
    case Keyword(name):
      return name
    case Environment():
      return '#<environment>'
    case Atomic() | Wrap() | Abstract():
      return '#<procedure>'
    case _:
      msg = f'Cannot show the unknown value {obj}.'
      raise error(msg)

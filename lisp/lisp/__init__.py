from typing import Optional
from typing import Callable
import dataclasses
import unittest

class Error(Exception):
  message: str
  object: Optional['Object']
  environment: Optional['Environment']

  def __init__(self, message, object=None, environment=None):
    self.message     = message
    self.object      = object
    self.environment = environment

  def __str__(self):
    return self.message

def error(message):
  return Error(message)

class Object:
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
  def is_environment(self):
    return False

  @property
  def is_procedure(self):
    return False

  @property
  def is_lift(self):
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

  def assert_environment(self):
    if not self.is_environment:
      message = f'Expected an environment, but got {self}.'
      raise error(message)

  def assert_procedure(self):
    if not self.is_procedure:
      message = f'Expected a procedure, but got {self}.'
      raise error(message)

  @property
  def to_lift(self):
    if not self.is_lift:
      message = f'Expected a lifted procedure, but got {self}.'
      raise error(message)
    return self.body

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
    message = f'The object {self} does not have an attribute named `body`.'
    raise error(message)

  @property
  def name(self):
    message = f'The object {self} does not have an attribute named `name`.'
    raise error(message)

  @property
  def value(self):
    message = f'The object {self} does not have an attribute named `value`.'
    raise error(message)

  @property
  def next(self):
    message = f'The object {self} does not have an attribute named `next`.'
    raise error(message)

  @property
  def head(self):
    message = f'The object {self} does not have an attribute named `head`.'
    raise error(message)

  @property
  def dynamic(self):
    message = f'The object {self} does not have an attribute named `dynamic`.'
    raise error(message)

  @property
  def lexical(self):
    message = f'The object {self} does not have an attribute named `lexical`.'
    raise error(message)

  @property
  def length(self):
    message = f'The object {Self} does not have an attribute named `length`.'
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

  def __eq__(self, rhs):
    return _equals(self, rhs)

class State:
  @property
  def is_ok(self):
    return False

  @property
  def is_eval(self):
    return False

  @property
  def is_evlis(self):
    return False

  @property
  def is_exec(self):
    return False

  @property
  def is_apply(self):
    return False

  def assert_ok(self):
    if not self.is_ok:
      message = f'Expected an ok state, but got {self}.'
      raise error(message)

Context = Callable[[Object], State]

@dataclasses.dataclass(frozen=True)
class Nil(Object):
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
class Pair(Object):
  __fst: Object
  __snd: Object

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

  def __contains__(self, object):
    self.assert_list()
    xs = self
    while not xs.is_nil:
      if object == xs.fst:
        return True
      xs = xs.snd
    return False

  def __getitem__(self, index):
    self.assert_list()
    xs = self
    while not xs.is_nil:
      if index == 0:
        return xs.fst
      index = index-1
      xs    = xs.snd
    message = f'List index out of bounds: {index}.'
    raise error(message)

  def __setitem__(self, index, value):
    message = f'Lists are immutable.'
    raise error(message)

@dataclasses.dataclass(frozen=True)
class Constant(Object):
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
class Variable(Object):
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
class Boolean(Object):
  __value: bool

  @property
  def is_boolean(self):
    return True

  @property
  def value(self):
    return self.__value

@dataclasses.dataclass(frozen=True)
class Number(Object):
  __value: float

  @property
  def is_number(self):
    return True

  @property
  def value(self):
    return self.__value

@dataclasses.dataclass(frozen=True)
class String(Object):
  __value: str

  @property
  def is_string(self):
    return True

  @property
  def value(self):
    return self.__value

class Environment(Object):
  __body: dict[str, Object]
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

  def __setitem__(self, key, value):
    match key:
      case Constant(name):
        msg = f'The symbol {name} is a constant and cannot be redefined.'
        raise error(msg)
      case Variable(name):
        if name in self.body:
          msg = f'The symbol {name} is already bound to a value and cannot be redefined.'
          raise error(msg)
        self.body[name] = value
      case str(name):
        if name[0].isupper():
          name = constant(name)
        else:
          name = variable(name)
        self[name] = value

@dataclasses.dataclass(frozen=True)
class Lift(Object):
  __body: Callable[[Object, Object, Context, 'Lisp'], State]

  @property
  def is_procedure(self):
    return True

  @property
  def is_lift(self):
    return True

  @property
  def body(self):
    return self.__body

@dataclasses.dataclass(frozen=True)
class Abstract(Object):
  __head: Object
  __body: Object
  __dynamic: Object
  __lexical: Object

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

@dataclasses.dataclass(frozen=True)
class Wrap(Object):
  __body: Object

  @property
  def is_procedure(self):
    return True

  @property
  def is_wrap(self):
    return True

  @property
  def body(self):
    return self.__body

@dataclasses.dataclass(frozen=True)
class Ok(State):
  object: Object

  @property
  def is_ok(self):
    return True

@dataclasses.dataclass(frozen=True)
class Eval(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_eval(self):
    return True

@dataclasses.dataclass(frozen=True)
class Evlis(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_evlis(self):
    return True

@dataclasses.dataclass(frozen=True)
class Exec(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_exec(self):
    return True

@dataclasses.dataclass(frozen=True)
class Apply(State):
  procedure: Object
  arguments: Object
  environment: Object
  ok: Context

  @property
  def is_apply(self):
    return True

def _lisp_list(args, env, go):
  def go_args(args):
    return go(args)
  return evlis(args, env, go_args)

def _lisp_vau(args, env, go):
  head    = args.fst
  body    = args.snd.snd
  dynamic = args.snd.fst
  lexical = env
  target  = abstract(head, body, dynamic, lexical)
  return go(target)

def _lisp_wrap(args, env, go):
  def go_args(args):
    return go(wrap(args.fst))
  return evlis(args, env, go_args)

def _lisp_unwrap(args, env, go):
  def go_args(args):
    return go(args.fst.to_wrap)
  return evlis(args, env, go_args)

def _lisp_add(args, env, go):
  def go_args(args):
    state = 0
    while not args.is_nil:
      state += args.fst.to_number
      args   = args.snd
    return go(number(state))
  return evlis(args, env, go_args)

def _lisp_mul(args, env, go):
  def go_args(args):
    state = 1
    while not args.is_nil:
      state *= args.fst.to_number
      args   = args.snd
    return go(number(state))
  return evlis(args, env, go_args)

def _lisp_sub(args, env, go):
  def go_args(args):
    if is_nil(args):
      msg = f'Subtraction requires at least one argument.'
      raise error(msg)
    state = args.fst.to_number
    args  = args.snd
    while not args.is_nil:
      state -= args.fst.to_number
      args   = args.snd
    return go(number(state))
  return evlis(args, env, go_args)

def _lisp_div(args, env, go):
  def go_args(args):
    if is_nil(args):
      msg = f'Division requires at least one argument.'
      raise error(msg)
    state = args.fst.to_number
    args  = args.snd
    while not args.is_nil:
      state /= args.fst.to_number
      args   = args.snd
    return go(number(state))
  return evlis(args, env, go_args)

def standard_environment():
  body = {}

  body['True']  = boolean(True)
  body['False'] = boolean(False)

  body['vau']    = lift(_lisp_vau)
  body['wrap']   = lift(_lisp_wrap)
  body['unwrap'] = lift(_lisp_unwrap)

  body['+'] = lift(_lisp_add)
  body['*'] = lift(_lisp_mul)
  body['-'] = lift(_lisp_sub)
  body['/'] = lift(_lisp_div)

  return environment(body)

def step(state):
  match state:
    case Ok():
      return state
    case Eval(value, env, go):
      match value:
        case Variable() | Constant():
          if value in env:
            rhs = env[value]
            return go(rhs)
          msg = f'The symbol {value} is undefined.'
          raise error(msg)
        case Pair(proc, args):
          def go_proc(proc):
            return apply(proc, args, env, go)
          return eval(proc, env, go_proc)
        case _:
          return go(value)
    case Evlis(value, env, go):
      match value:
        case Nil():
          return go(value)
        case Pair(fst, snd):
          def go_fst(fst):
            def go_snd(snd):
              return go(pair(fst, snd))
            return evlis(snd, env, go_snd)
          return eval(fst, env, go_fst)
        case _:
          msg = f'Expected a list, but got {value}.'
          raise error(msg)
    case Exec(value, env, go):
      match value:
        case Nil():
          return go(value)
        case Pair(fst, snd):
          def go_fst(fst):
            def go_snd(snd):
              if not snd.is_nil:
                return go(snd)
              return go(fst)
            return exec(snd, env, go_snd)
          return eval(fst, env, go_fst)
        case _:
          msg = f'Expected a list, but got {value}.'
          raise error(msg)
    case Apply(proc, args, env, go):
      match proc:
        case Lift(body):
          return body(args, env, go)
        case Abstract(head, body, dynamic, lexical):
          if head.length != args.length:
            msg = f'Expected {head.length} arguments, but got {args.length}.'
            raise error(msg)
          local = environment(next=lexical)
          while not head.is_nil:
            lhs        = head.fst.to_variable
            rhs        = args.fst
            local[lhs] = rhs
            head       = head.snd
            args       = args.snd
          local[dynamic] = env
          return exec(body, local, go)
        case Wrap(proc):
          def go_args(args):
            return apply(proc, args, env, go)
          return evlis(args, env, go_args)
        case _:
          msg = f'Expected to apply a procedure, but got {proc}.'
          raise error(msg)

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

def lift(body):
  return Lift(body)

def abstract(head, body, dynamic, lexical):
  head.assert_list()
  body.assert_list()
  dynamic.assert_variable()
  lexical.assert_environment()
  return Abstract(head, body, dynamic, lexical)

def wrap(body):
  body.assert_procedure()
  return Wrap(body)

def ok(object):
  return Ok(object)

def eval(value, env=None, go=ok):
  if env is None:
    env = standard_environment()
  else:
    env.assert_environment()
  return Eval(value, env, go)

def evlis(value, env=None, go=ok):
  if env is None:
    env = standard_environment()
  else:
    env.assert_environment()
  value.assert_list()
  return Evlis(value, env, go)

def exec(value, env=None, go=None):
  if env is None:
    env = standard_environment()
  else:
    env.assert_environment()
  value.assert_list()
  return Exec(value, env, go)

def apply(proc, args, env=None, go=None):
  if env is None:
    env = standard_environment()
  else:
    env.assert_environment()
  proc.assert_procedure()
  args.assert_list()
  return Apply(proc, args, env, go)

def read(source: str):
  stack = []
  build = []
  index = 0

  def seek_while(fn):
    nonlocal source
    nonlocal index
    while index < len(source) and fn(source[index]):
      index += 1

  def seek_until(fn):
    nonlocal source
    nonlocal index
    while index < len(source) and not fn(source[index]):
      index += 1

  is_lparen     = lambda x: x == '('
  is_rparen     = lambda x: x == ')'
  is_paren      = lambda x: x in ['(', ')']
  is_quote      = lambda x: x == '"'
  is_whitespace = lambda x: x in [' ', '\t', '\r', '\n']
  is_separator  = lambda x: is_paren(x) or is_quote(x) or is_whitespace(x)
  is_unreadable = lambda x: x.startswith('#<')
  is_constant   = lambda x: x[0].isupper()

  while index < len(source):
    if is_lparen(source[index]):
      stack.append(build)
      build = []
      index += 1
    elif is_rparen(source[index]):
      if len(stack) == 0:
        msg = f'Unbalanced parentheses within source code:\n{source}'
        raise error(msg)
      xs = from_list(build)
      build = stack.pop()
      build.append(xs)
      index += 1
    elif is_quote(source[index]):
      index += 1
      start  = index
      seek_until(is_quote)
      body = source[start:index]
      build.append(string(body))
      index += 1
    elif is_whitespace(source[index]):
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
    case String(value):
      # todo: escape quotes
      return f'"{value}"'
    case Environment():
      return '#<environment>'
    case Lift() | Wrap() | Abstract():
      return '#<procedure>'
    case _:
      msg = f'Cannot show the unknown object {obj}.'
      raise error(msg)

def _equals(lhs, rhs):
  match lhs:
    case Nil():
      return rhs.is_nil
    case Pair(lhs_fst, lhs_snd):
      match rhs:
        case Pair(rhs_fst, rhs_snd):
          if _equals(lhs_fst, rhs_fst):
            return _equals(lhs_snd, rhs_snd)
          return False
        case _:
          return False
    case Constant(lhs_name):
      match rhs:
        case Constant(rhs_name):
          return lhs_name == rhs_name
        case _:
          return False
    case Variable(lhs_name):
      match rhs:
        case Variable(rhs_name):
          return lhs_name == rhs_name
        case _:
          return False
    case Boolean(lhs_value):
      match rhs:
        case Boolean(rhs_value):
          return lhs_value == rhs_value
        case _:
          return False
    case Number(lhs_value):
      match rhs:
        case Number(rhs_value):
          return _isclose(lhs_value, rhs_value)
        case _:
          return False
    case String(lhs_value):
      match rhs:
        case String(rhs_value):
          return lhs_value == rhs_value
        case _:
          return False
    case Environment() | Lift() | Abstract() | Wrap():
      return lhs == rhs
    case _:
      raise error(f'Cannot determine the equality of the unknown object {lhs}.')

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

class SanityTest(unittest.TestCase):
  def test_read(self):
    examples = [
      'foo',
      'Bar',
      '3.14',
      'True',
      'False',
      '"Hello, world."',
      '(+ 1.0 2.0 3.0 4.0)',
    ]
    for example in examples:
      obj = read(example)[0]
      self.assertEqual(example, f'{obj}')

  def test_eval(self):
    examples = [
      ['(vau (x) e x)', lambda x: x.is_procedure],
      ['((vau (x) e x) 3)', lambda x: x.to_number == 3],
      ['(wrap (vau (x) e x))', lambda x: x.is_procedure],
      ['(unwrap (wrap (vau (x) e x)))', lambda x: x.is_procedure],
      ['(+ 1 2 3 4)', lambda x: x.to_number == 10],
      ['(* 1 2 3 4)', lambda x: x.to_number == 24],
    ]
    for initial, measure in examples:
      object = read(initial)[0]
      gas    = 100
      state  = eval(object)
      while gas > 0 and not state.is_ok:
        gas  -= 1
        state = step(state)
      self.assertTrue(state.is_ok)
      self.assertTrue(measure(state.object))

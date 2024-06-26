from typing import Optional
from typing import Callable
import dataclasses

class Error(Exception):
  body: dict[str, object]

  def __init__(self, body):
    self.body = body

  def __str__(self):
    pass

def error(data):
  return Error(data)

def unexpected(actual, expected):
  err = {
    'message': f'''
Expected `{expected}`, but got `{actual}`.
'''.strip(),
    'expected': expected,
    'actual': actual,
  }
  return error(err)

def out_of_bounds(collection, index):
  pass

def cannot_apply(proc, args, env, err):
  pass

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
  def is_advice(self):
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
      raise unexpected(self, 'nil')

  def assert_pair(self):
    if not self.is_nil:
      raise unexpected(self, 'pair')

  def assert_list(self):
    if not self.is_list:
      raise unexpected(self, 'list')

  def assert_symbol(self):
    if not self.is_symbol:
      raise unexpected(self, 'symbol')

  def assert_constant(self):
    if not self.is_constant:
      raise unexpected(self, 'constant')

  def assert_variable(self):
    if not self.is_variable:
      raise unexpected(self, 'variable')

  def assert_boolean(self):
    if not self.is_boolean:
      raise unexpected(self, 'boolean')

  def assert_number(self):
    if not self.is_number:
      raise unexpected(self, 'Number?')

  def assert_string(self):
    if not self.is_string:
      raise unexpected(self, 'String?')

  def assert_keyword(self):
    if not self.is_keyword:
      raise unexpected(self, 'Keyword?')

  def assert_environment(self):
    if not self.is_environment:
      raise unexpected(self, 'Environment?')

  def assert_advice(self):
    if not self.is_advice:
      raise unexpected(self, 'Advice?')

  def assert_procedure(self):
    if not self.is_procedure:
      raise unexpected(self, 'Procedure?')

  @property
  def to_constant(self):
    self.assert_constant()
    return self.name

  @property
  def to_variable(self):
    self.assert_variable()
    return self.name

  @property
  def to_boolean(self):
    self.assert_boolean()
    return self.value

  @property
  def to_number(self):
    self.assert_number()
    return self.value

  @property
  def to_string(self):
    self.assert_string()
    return self.value

  @property
  def to_keyword(self):
    self.assert_keyword()
    return self.value

  @property
  def to_wrap(self):
    self.assert_wrap()
    return self.body

  @property
  def fst(self):
    raise unexpected(self, 'Pair?')

  @property
  def snd(self):
    raise unexpected(self, 'Pair?')

  @property
  def body(self):
    raise unexpected(self, '--body?')

  @property
  def name(self):
    raise unexpected(self, '(or Constant? Symbol?)')

  @property
  def value(self):
    raise unexpected(self, '--value?')

  @property
  def next(self):
    raise unexpected(self, '--next?')

  @property
  def head(self):
    raise unexpected(self, 'abstract')

  @property
  def dynamic(self):
    raise unexpected(self, 'abstract')

  @property
  def lexical(self):
    raise unexpected(self, 'abstract')

  @property
  def length(self):
    raise unexpected(self, '--length?')

  def __contains__(self, key):
    raise unexpected(self, '--collection?')

  def __getitem__(self, key):
    raise unexpected(self, '--collection?')

  def __setitem__(self, key, value):
    raise unexpected(self, '--collection?')

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

  def __getitem__(self, index):
    raise out_of_bounds(self, index)

  def __setitem__(self, key, value):
    raise cannot_mutate(self, key, value)

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
    xs    = self
    while not xs.is_nil:
      if state == 0:
        return xs.fst
      state = state-1
      xs    = xs.snd
    xs.assert_nil()
    raise out_of_bounds(self, index)

  def __setitem__(self, index, value):
    raise cannot_mutate(self, index, value)

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
  def value(self):
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
        raise undefined(self, key)
      case Variable(name):
        env = self
        while env is not None:
          if name in env.body:
            return env.body[name]
          env = env.next
        assert env is None
        raise undefined(self, key)
      case str(name):
        if name[0].isupper():
          name = constant(name)
        else:
          name = variable(name)
        return self[name]
      case _:
        raise undefined(self, key)

  def __setitem__(self, key, value):
    match key:
      case Nil():
        match value:
          case Nil():
            pass
          case _:
            raise unexpected(value, 'nil')
      case Constant(name):
        raise redefined(self, key, value)
      case Variable(name):
        if name in self.body:
          raise redefined(self, key, value)
        self.body[name] = value
      case Keyword(name):
        match name:
          case ':none':
            pass
          case _:
            raise unexpected(key, '--grammar?')
      case str(name):
        if name[0].isupper():
          name = constant(name)
        elif name[0] == ':':
          name = keyword(name)
        else:
          name = variable(name)
        self[name] = value
      case _:
        raise unexpected(key, '--can-bind?')

@dataclasses.dataclass(frozen=True, eq=False)
class Advice(Value):
  __body: Value
  __next: Value

  @property
  def is_advice(self):
    return True

  @property
  def body(self):
    return self.__body

  @property
  def next(self):
    return self.__next

@dataclasses.dataclass(frozen=True, eq=False)
class Atomic(Value):
  @property
  def is_procedure(self):
    return True

  @property
  def is_atomic(self):
    return True

  @property
  def help(self):
    signature = f'({self.name} {self.parameters})'
    data = {
      'name': self.name,
      'signature': signature,
      'comment', self.comment,
    }
    return from_dict(data)

@dataclasses.dataclass(frozen=True, eq=False)
class Abstract(Value):
  __head: Value
  __body: Value
  __dynamic: Value
  __lexical: Value
  __help: Value

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

  @property
  def help(self):
    return self.__help

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

  @property
  def help(self):
    return self.body.help

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
    raise no_construct('environment', body, next)
  if next is not None:
    next.assert_environment()
  return Environment(body, next)

def advice(body, next=None):
  body.assert_list()
  if next is not None:
    next.assert_advice()
  return Advice(body, next)

def atomic(body):
  return Atomic(body)

def abstract(head, body, dynamic, lexical):
  head.assert_can_bind()
  body.assert_list()
  dynamic.assert_can_bind()
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
        raise unbalanced_parens(source, index)
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
        raise unreadable_symbol(source, index, body)
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
      raise no_show(obj)

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

Context = Callable[[Value], State]

@dataclasses.dataclass(frozen=True)
class Ok(State):
  value: Value

  @property
  def is_ok(self):
    return True

  def __str__(self):
    return f'#<ok {self.value}>'

@dataclasses.dataclass(frozen=True)
class Eval(State):
  value: Value
  environment: Value
  advice: Value
  go: Context

  @property
  def is_eval(self):
    return True

  def __str__(self):
    return f'#<eval {self.value}>'

@dataclasses.dataclass(frozen=True)
class Evlis(State):
  value: Value
  environment: Value
  advice: Value
  go: Context

  @property
  def is_evlis(self):
    return True

  def __str__(self):
    return f'#<evlis {self.value}>'

@dataclasses.dataclass(frozen=True)
class Exec(State):
  value: Value
  environment: Value
  advice: Value
  go: Context

  @property
  def is_exec(self):
    return True

  def __str__(self):
    return f'#<exec {self.value}>'

@dataclasses.dataclass(frozen=True)
class Apply(State):
  procedure: Value
  arguments: Value
  environment: Value
  advice: Value
  go: Context

  @property
  def is_apply(self):
    return True

  def __str__(self):
    return f'#<apply {self.value}>'

@dataclasses.dataclass(frozen=True)
class Consult(State):
  rules: Value
  point: Value
  value: Value
  environment: Value
  advice: Value
  go: Context

  @property
  def is_consult(self):
    return True

  def __str__(self):
    return f'#<state:consult>'

def ok(value):
  return Ok(value)

def eval(value, env, adv, go=ok):
  env.assert_environment()
  return Eval(value, env, adv, go)

def evlis(value, env, adv, go=ok):
  env.assert_environment()
  value.assert_list()
  return Evlis(value, env, adv, go)

def exec(value, env, adv, go=None):
  env.assert_environment()
  value.assert_list()
  return Exec(value, env, adv, go)

def apply(proc, args, env, adv, go=None):
  env.assert_environment()
  proc.assert_procedure()
  args.assert_list()
  return Apply(proc, args, env, go)

def consult(rules, point, value, env, adv, go):
  rules.assert_list()
  env.assert_environment()
  adv.assert_advice()
  return Consult(rules, point, env, adv, go)

def step(state):
  match state:
    case Ok():
      return state
    case Eval(value, env, adv, fx, go):
      match value:
        case Variable() | Constant():
          if value in env:
            rhs = env[value]
            return go(rhs)
          msg = f'The symbol {value} is undefined.'
          raise error(msg)
        case Pair(proc, args):
          def go_proc(proc):
            if adv is not None:
              rules  = adv.body
              point  = adv
              value_ = pair(proc, args)
              return consult(rules, point, value_, env, adv, go)
            return apply(proc, args, env, go)
          return eval(proc, env, go_proc)
        case _:
          return go(value)
    case Evlis(value, env, adv, fx, go):
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
    case Consult(rules, point, value, env, adv, go):
      if rules.is_nil:
        if point.next is None:
          match value:
            # TODO: should advice be able to completely
            # suppress an application like this?
            case Nil():
              return go(value)
            case Pair(proc, args):
              return apply(proc, args, env, adv, go)
            case _:
              message = f'''

'''.strip()
              raise error(message)
        point_ = point.next
        rules_ = point_.body
        return consult(rules_, point_, value, env, adv, go)
      cond   = rules.fst.fst
      func   = rules.fst.snd.fst
      rest   = rules.snd
      point_ = point.next
      def go_cond(test):
        if test.to_boolean:
          def go_func(value):
            rules = point.body
            return consult(rules, point, value, env, adv, go)
          return apply(func, value, env, point_, go_func)
        return consult(rest, point, value, env, adv, go)
      return apply(cond, value, env, point_, go_cond) 
    case Apply(proc, args, env, go):
      match proc:
        case Atomic():
          # print(proc.comment)
          if proc.is_applicative:
            def go_args(args):
              try:
                return proc(args, env, go)
              except Error as err:
                raise atomic_error(proc, args, env, err)
            return evlis(args, env, go_args)
          else:
            try:
              return proc(args, env, go)
            except Error as err:
              raise atomic_error(proc, args, env, err)
        case Abstract(head, body, dynamic, lexical):
          try:
            local = environment(next=lexical)
            if head.is_list:
              # TODO you can't just check the lengths of the two lists bc of
              # things like :rest, but failing if xs isn't nil at the end isn't
              # very informative...
              xs = args
              while not head.is_nil:
                lhs        = head.fst.to_variable
                rhs        = xs.fst
                local[lhs] = rhs
                head       = head.snd
                xs         = xs.snd
              xs.assert_nil()
            else:
              local[head] = args
            local[dynamic] = env
            return exec(body, local, go)
          except Error as err:
            raise abstract_error(proc, args, env, err)
        case Wrap(proc):
          def go_args(args):
            return apply(proc, args, env, go)
          return evlis(args, env, go_args)
        case _:
          msg = f'Expected to apply a procedure, but got {proc}.'
          raise error(msg)

def norm(initial, env, quota=1_000):
  state = eval(initial, env)
  while quota > 0 and not state.is_ok:
    quota -= 1
    state  = step(state)
  state.assert_ok()
  return state.value

import dataclasses
import scriptkitty.engine.lisp.kernel as kernel

@dataclasses.dataclass(frozen=True)
class Print(kernel.Atomic):
  @property
  def name(self):
    return 'print'

  @property
  def parameters(self):
    return 'VALUE...'

  @property
  def comment(self):
    return f'''
Write the string representation of each VALUE to standard output.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, adv, fx, go):
    buf = []
    while not args.is_nil:
      buf.append(str(args.fst))
      args = args.snd
    string = ' '.join(buf)
    fx.print(string)
    return go(kernel.nil())

@dataclasses.dataclass(frozen=True)
class List(kernel.Atomic):
  @property
  def name(self):
    return 'list'

  @property
  def parameters(self):
    return 'VALUE...'

  @property
  def comment(self):
    return f'''
Return a list containing each VALUE, in order from left to right.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, adv, fx, go):
    return go(args)

@dataclasses.dataclass(frozen=True)
class ListStar(kernel.Atomic):
  @property
  def name(self):
    return 'list*'

  @property
  def parameters(self):
    return 'VALUE...'

  @property
  def comment(self):
    return f'''
Return a list of the VALUEs, where the last VALUE is the tail of the list.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, adv, fx, go):
    if args.is_nil:
      return go(args)
    if args.snd.is_nil:
      return go(args.fst)
    buf = []
    while not args.snd.is_nil:
      buf.append(args.fst)
      args = args.snd
    state = args.fst
    for value in reversed(buf):
      state = kernel.pair(value, state)
    return go(state)

@dataclasses.dataclass(frozen=True)
class Fst(kernel.Atomic):
  @property
  def name(self):
    return 'fst'

  @property
  def parameters(self):
    return 'PAIR'

  @property
  def comment(self):
    return f'''
Return the first element of PAIR.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.fst)

@dataclasses.dataclass(frozen=True)
class Snd(kernel.Atomic):
  @property
  def name(self):
    return 'snd'

  @property
  def parameters(self):
    return 'PAIR'

  @property
  def comment(self):
    return f'''
Return the second element of PAIR.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.snd)

@dataclasses.dataclass(frozen=True)
class Define(kernel.Atomic):
  @property
  def parameters(self):
    return 'NAME VALUE'

  @property
  def comment(self):
    return f'''
Associates NAME with VALUE in the current environment.
Raises an error if NAME is already associated with another
value within the current environment.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    lhs = args.fst
    rhs = args.snd.fst
    def go_rhs(rhs):
      env[lhs] = rhs
      return go(kernel.nil())
    return kernel.eval(rhs, env, go_rhs)

@dataclasses.dataclass(frozen=True)
class Let(kernel.Atomic):
  @property
  def parameters(self):
    return 'BINDINGS BODY...'

  @property
  def comment(self):
    return f'''
BINDINGS is an association list of key-value pairs; each
key is bound to the corresponding value within a new
environment; then, BODY is executed within this environment.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    bindings = args.fst
    body     = args.snd
    scope    = kernel.environment(next=env)
    def iter(bindings):
      match bindings:
        case kernel.Nil():
          return kernel.exec(body, scope, go)
        case kernel.Pair(assoc, rest):
          key   = assoc.fst
          value = assoc.snd.fst
          def go_value(value):
            nonlocal scope
            scope[key] = value
            return iter(rest)
          return kernel.eval(value, scope, go_value)
        case _:
          raise unreachable(self, args, env, go)
    return iter(bindings)

@dataclasses.dataclass(frozen=True)
class Eval(kernel.Atomic):
  @property
  def parameters(self):
    return 'EXPRESSION ENVIRONMENT?'

  @property
  def comment(self):
    return f'''
Evaluate EXPRESSION in ENVIRONMENT (if it is provided) or the current environment
if it is not.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    expr = args.fst
    if args.snd.is_nil:
      return kernel.eval(expr, env, go)
    local = args.snd.fst
    def go_local(local):
      return kernel.eval(expr, local, go)
    return kernel.eval(local, env, go_local)

@dataclasses.dataclass(frozen=True)
class Vau(kernel.Atomic):
  @property
  def parameters(self):
    return 'PARAMETERS ENVIRONMENT BODY...'

  @property
  def comment(self):
    return f'''
Returns a new abstract procedure that binds PARAMETERS
and ENVIRONMENT at the call site within a new scope and
then evaluates BODY within that scope.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    head    = args.fst
    body    = args.snd.snd
    dynamic = args.snd.fst
    lexical = env
    return go(kernel.abstract(head, body, dynamic, lexical))

@dataclasses.dataclass(frozen=True)
class Wrap(kernel.Atomic):
  @property
  def parameters(self):
    return 'PROCEDURE'

  @property
  def comment(self):
    return f'''
Returns a procedure that first evaluates all of its arguments,
and then calls PROCEDURE on the results.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(kernel.wrap(args.fst))

@dataclasses.dataclass(frozen=True)
class Unwrap(kernel.Atomic):
  @property
  def parameters(self):
    return 'PROCEDURE'
  
  @property
  def comment(self):
    return f'''
If PROCEDURE was created with WRAP then this procedure will
return its body; if not then an error is raised.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.to_wrap)

@dataclasses.dataclass(frozen=True)
class Add(kernel.Atomic):
  @property
  def name(self):
    return '+'

  @property
  def parameters(self):
    return 'NUMBER...'

  @property
  def comment(self):
    return f'''
Folds the list of numbers with addition, using 0 as the initial state.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    state = 0
    while not args.is_nil:
      state += args.fst.to_number
      args   = args.snd
    return go(kernel.number(state))

@dataclasses.dataclass(frozen=True)
class Mul(kernel.Atomic):
  @property
  def name(self):
    return '*'

  @property
  def parameters(self):
    return 'NUMBER...'

  @property
  def comment(self):
    return f'''
Folds the list of numbers with multiplication, using 1 as the initial state.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    state = 1
    while not args.is_nil:
      state *= args.fst.to_number
      args   = args.snd
    return go(kernel.number(state))

@dataclasses.dataclass(frozen=True)
class Sub(kernel.Atomic):
  @property
  def name(self):
    return '-'

  @property
  def parameters(self):
    return 'INITIAL-NUMBER NUMBER...'

  @property
  def comment(self):
    return f'''
Folds the list of numbers with subtraction, using the first number as
the initial state; there must be at least one number or an error is raised.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    state = args.fst.to_number
    args  = args.snd
    while not args.is_nil:
      state -= args.fst.to_number
      args   = args.snd
    return go(kernel.number(state))

@dataclasses.dataclass(frozen=True)
class Div(kernel.Atomic):
  @property
  def name(self):
    return '/'

  @property
  def parameters(self):
    return 'INITIAL-NUMBER NUMBER...'

  @property
  def comment(self):
    return f'''
Folds the list of numbers with division, using the first number as
the initial state; there must be at least one number or an error is raised.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    state = args.fst.to_number
    args  = args.snd
    while not args.is_nil:
      value  = args.fst.to_number
      if value == 0:
        # TODO: lol we could say x/0 == 0, a few people did this
        raise kernel.error('Division by zero.')
      else:
        state /= value
      args = args.snd
    return go(kernel.number(state))

@dataclasses.dataclass(frozen=True)
class And(kernel.Atomic):
  @property
  def name(self):
    return 'and'

  @property
  def parameters(self):
    return 'CONDITION...'
  
  @property
  def comment(self):
    return f'''
Evaluates each condition from left to right. If a condition returns false
then this procedure returns false; if no condition returns false then
this procedure returns true.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    def iter(args):
      if args.is_nil:
        return go(kernel.boolean(True))
      def go_fst(fst):
        if not fst.to_boolean:
          return go(kernel.boolean(False))
        return iter(args.snd)
      return kernel.eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class Or(kernel.Atomic):
  @property
  def name(self):
    return 'or'

  @property
  def parameters(self):
    return 'CONDITION...'

  @property
  def comment(self):
    return f'''
Evaluates each condition from left to right. If a condition returns true
then this procedure returns true; if no condition returns false then
this procedure returns false.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    def iter(args):
      if args.is_nil:
        return go(kernel.boolean(False))
      def go_fst(fst):
        if fst.to_boolean:
          return go(kernel.boolean(True))
        return iter(args.snd)
      return kernel.eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class Not(kernel.Atomic):
  @property
  def name(self):
    return 'not'

  @property
  def parameters(self):
    return 'BOOLEAN'

  @property
  def comment(self):
    return f'''
If BOOLEAN is True, return False; if BOOLEAN is False, returns True.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(kernel.boolean(not args.fst.to_boolean))

# Operations that work on both association lists and dictionaries (TODO)
class Get(kernel.Atomic):
  @property
  def name(self):
    return 'get'

  @property
  def parameters(self):
    return 'COLLECTION KEY'

  @property
  def comment(self):
    return f'''

'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, adv, go):
    data = args.fst
    expected_key = args.snd.fst
    while not data.is_nil:
      pair = data.fst
      actual_key = pair.fst
      value = pair.snd.fst
      if actual_key == expected_key:
        return go(value)
      data = data.snd
    return go(kernel.nil())

class IsString(kernel.Atomic):
  @property
  def name(self):
    return 'String?'

  @property
  def parameters(self):
    return 'OBJECT'

  @property
  def comment(self):
    return f'''
Returns True if OBJECT is a string, and False otherwise.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, adv, fx, go):
    match args.fst:
      case kernel.String(_):
        return go(kernel.true)
      case _:
        return go(kernel.false)

def initial_environment():
  body = {}

  body['True']  = kernel.boolean(True)
  body['False'] = kernel.boolean(False)

  initial_procedures = [
    Print(),
    Define(),
    Let(),
    Eval(),
    Vau(),
    Wrap(),
    Unwrap(),
    List(),
    ListStar(),
    Fst(),
    Snd(),
    Add(),
    Mul(),
    Sub(),
    Div(),
    And(),
    Or(),
    Not(),
  ]

  for procedure in initial_procedures:
    body[procedure.name] = procedure

  return kernel.environment(body)

import scriptkitty.engine.lisp as lisp

if __name__ == '__main__':
  context = lisp.initial_environment()
  while True:
    try:
      source  = input('lisp@1.0.0:/\nλ ')
      values = lisp.read(source)
      for value in values:
        target = lisp.norm(value, context)
        print(target)
    except Error as err:
      print(err)

from scriptkitty.engine.lisp.value import Value
from scriptkitty.engine.lisp.value import Nil
from scriptkitty.engine.lisp.value import Pair
from scriptkitty.engine.lisp.value import Constant
from scriptkitty.engine.lisp.value import Variable
from scriptkitty.engine.lisp.value import Boolean
from scriptkitty.engine.lisp.value import Number
from scriptkitty.engine.lisp.value import String
from scriptkitty.engine.lisp.value import Keyword
from scriptkitty.engine.lisp.value import Environment
from scriptkitty.engine.lisp.value import Atomic
from scriptkitty.engine.lisp.value import Abstract
from scriptkitty.engine.lisp.value import Wrap
from scriptkitty.engine.lisp.value import Error
from scriptkitty.engine.lisp.value import nil
from scriptkitty.engine.lisp.value import pair
from scriptkitty.engine.lisp.value import list
from scriptkitty.engine.lisp.value import constant
from scriptkitty.engine.lisp.value import variable
from scriptkitty.engine.lisp.value import keyword
from scriptkitty.engine.lisp.value import boolean
from scriptkitty.engine.lisp.value import number
from scriptkitty.engine.lisp.value import string
from scriptkitty.engine.lisp.value import environment
from scriptkitty.engine.lisp.value import atomic
from scriptkitty.engine.lisp.value import abstract
from scriptkitty.engine.lisp.value import wrap
from scriptkitty.engine.lisp.value import from_list
from scriptkitty.engine.lisp.value import from_dict
from scriptkitty.engine.lisp.value import read

from scriptkitty.engine.lisp.value import State
from scriptkitty.engine.lisp.value import Context
from scriptkitty.engine.lisp.value import Ok
from scriptkitty.engine.lisp.value import Eval
from scriptkitty.engine.lisp.value import Evlis
from scriptkitty.engine.lisp.value import Exec
from scriptkitty.engine.lisp.value import Apply
from scriptkitty.engine.lisp.value import ok
from scriptkitty.engine.lisp.value import eval
from scriptkitty.engine.lisp.value import evlis
from scriptkitty.engine.lisp.value import exec
from scriptkitty.engine.lisp.value import apply
from scriptkitty.engine.lisp.value import step
from scriptkitty.engine.lisp.value import norm

from scriptkitty.engine.lisp.procedure import initial_environment

import random
import unittest

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
      value = read(example)[0]
      self.assertEqual(example, f'{value}')

  def test_norm(self):
    examples = [
      ['(vau (x) e x)', lambda x: x.is_procedure],
      ['((vau (x) e x) 3)', lambda x: x.to_number == 3],
      ['(wrap (vau (x) e x))', lambda x: x.is_procedure],
      ['(unwrap (wrap (vau (x) e x)))', lambda x: x.is_procedure],
      ['(+ 1 2 3 4)', lambda x: x.to_number == 10],
      ['(* 1 2 3 4)', lambda x: x.to_number == 24],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final   = norm(initial, initial_environment())
      self.assertTrue(measure(final))

  def test_nested_operations(self):
    source = '(+ 1 (* 2 3) (- 10 6))'
    initial = read(source)[0]
    final = norm(initial, initial_environment())
    self.assertTrue(final.to_number == 11)

  def test_add_and_subtract(self):
    examples = [
      ['(+)', lambda x: x.to_number == 0],
      ['(+ 1 2 3 4 5)', lambda x: x.to_number == 15],
      ['(- 10)', lambda x: x.to_number == 10],
      ['(- 10 5)', lambda x: x.to_number == 5],
      ['(- 10 3 2)', lambda x: x.to_number == 5],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial, initial_environment())
      self.assertTrue(measure(final))

  def test_multiply_and_divide(self):
    examples = [
      ['(*)', lambda x: x.to_number == 1],
      ['(* 1 2 3 4 5)', lambda x: x.to_number == 120],
      ['(/ 100)', lambda x: x.to_number == 100],
      ['(/ 100 5)', lambda x: x.to_number == 20],
      ['(/ 120 2 3)', lambda x: x.to_number == 20],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial, initial_environment())
      self.assertTrue(measure(final))

  def test_vau_wrap_unwrap(self):
    examples = [
      ['(vau (x) e x)', lambda x: x.is_procedure],
      ['(wrap (vau (x) e x))', lambda x: x.is_procedure and x.is_wrap],
      ['(unwrap (wrap (vau (x) e x)))', lambda x: x.is_procedure and not x.is_wrap],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial, initial_environment())
      self.assertTrue(measure(final))

  def test_miscellaneous_operations(self):
    examples = [
      ['(+ 1 (* 2 3) (- 5 3))', lambda x: x.to_number == 9],
      ['(+ (* 2 (/ 8 4)) (- 10 8))', lambda x: x.to_number == 6],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial, initial_environment())
      self.assertTrue(measure(final))

  def test_string_escapes(self):
    strings = [
      '"He said \\"Hello, world.\\""',
    ]
    for string in strings:
      value = read(string)[0]
      iterations = random.randint(1, 10)
      for _ in range(iterations):
        value = read(f'{value}')[0]
      #print(f'\nstring={string}\nvalue={value}')
      self.assertEqual(f'{value}', string)

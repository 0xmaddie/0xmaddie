from typing import Optional
from typing import Callable
import random
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
    message = f'The object {self} does not have an attribute named `length`.'
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
    #string = self.__value.replace('"', '\\"')
    #return string
    string = self.__value
    return f'"{string}"'

@dataclasses.dataclass(frozen=True)
class Keyword(Object):
  __value: str

  @property
  def is_keyword(self):
    return True

  @property
  def value(Self):
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
class Atomic(Object):
  @property
  def is_procedure(self):
    return True

  @property
  def is_atomic(self):
    return True

@dataclasses.dataclass(frozen=True, eq=False)
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

@dataclasses.dataclass(frozen=True, eq=False)
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

  def __str__(self):
    return f'#<ok {self.object}>'

@dataclasses.dataclass(frozen=True)
class Eval(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_eval(self):
    return True

  def __str__(self):
    return f'#<eval {self.object}>'

@dataclasses.dataclass(frozen=True)
class Evlis(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_evlis(self):
    return True

  def __str__(self):
    return f'#<evlis {self.object}>'

@dataclasses.dataclass(frozen=True)
class Exec(State):
  object: Object
  environment: Object
  ok: Context

  @property
  def is_exec(self):
    return True

  def __str__(self):
    return f'#<exec {self.object}>'

@dataclasses.dataclass(frozen=True)
class Apply(State):
  procedure: Object
  arguments: Object
  environment: Object
  ok: Context

  @property
  def is_apply(self):
    return True

  def __str__(self):
    return f'#<apply {self.object}>'

@dataclasses.dataclass(frozen=True)
class PrPrint(Atomic):
  @property
  def advice(self):
    return f'''
(print OBJECT...)

Write the string representation of each OBJECT to standard output.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    buf = []
    while not args.is_nil:
      buf.append(str(args.fst))
      args = args.snd
    string = ' '.join(buf)
    print(string)
    return go(nil())

@dataclasses.dataclass(frozen=True)
class PrList(Atomic):
  @property
  def advice(self):
    return f'''
(list OBJECT...)

Return a list containing each OBJECT, in order from left to right.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args)

@dataclasses.dataclass(frozen=True)
class PrListStar(Atomic):
  @property
  def advice(self):
    return f'''
(list* OBJECT...)

Return a list of the OBJECTs, where the last OBJECT is the tail of the list.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    if args.is_nil:
      return go(args)
    if args.snd.is_nil:
      return go(args.fst)
    buf = []
    while not args.snd.is_nil:
      buf.append(args.fst)
      args = args.snd
    state = args.fst
    for object in reversed(buf):
      state = pair(object, state)
    return go(state)

@dataclasses.dataclass(frozen=True)
class PrFst(Atomic):
  @property
  def advice(self):
    return f'''
(fst PAIR)

Return the first element of PAIR.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.fst)

@dataclasses.dataclass(frozen=True)
class PrSnd(Atomic):
  @property
  def advice(self):
    return f'''
(snd PAIR)

Return the second element of PAIR.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.fst)

@dataclasses.dataclass(frozen=True)
class PrDefine(Atomic):
  @property
  def advice(self):
    return f'''
(define NAME OBJECT)

Associates NAME with OBJECT in the current environment.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    lhs = args.fst
    rhs = args.snd.fst
    def go_rhs(rhs):
      env[lhs] = rhs
      return go(nil())
    return eval(rhs, env, go_rhs)

@dataclasses.dataclass(frozen=True)
class PrLet(Atomic):
  @property
  def advice(self):
    return f'''
(let BINDINGS BODY...)

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
    scope    = environment(next=env)
    def iter(bindings):
      if bindings.is_nil:
        return exec(body, scope, go)
      pair = bindings.fst
      lhs  = pair.fst
      rhs  = pair.snd.fst
      def go_rhs(rhs):
        nonlocal scope
        scope[lhs] = rhs
        return iter(bindings.snd)
      return eval(rhs, scope, go_rhs)
    return iter(bindings)

@dataclasses.dataclass(frozen=True)
class PrEval(Atomic):
  @property
  def advice(self):
    return f'''
(eval EXPRESSION ENVIRONMENT?)

Evaluate EXPRESSION in ENVIRONMENT (if it is provided) or the current environment
if it is not.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    expr = args.fst
    if not args.snd.is_nil:
      scope = args.snd.fst
      def go_scope(scope):
        return eval(expr, scope, go)
      return eval(scope, env, go_scope)
    else:
      scope = initial_environment()
      return eval(expr, scope, go)

@dataclasses.dataclass(frozen=True)
class PrVau(Atomic):
  @property
  def advice(self):
    return f'''
(vau FORMAL-PARAMETERS FORMAL-ENVIRONMENT BODY...)

Returns a new abstract procedure that binds FORMAL-PARAMETERS
and FORMAL-ENVIRONMENT at the call site within a new scope and
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
    return go(abstract(head, body, dynamic, lexical))

@dataclasses.dataclass(frozen=True)
class PrWrap(Atomic):
  @property
  def advice(self):
    return f'''
(wrap PROCEDURE)

Returns a procedure that first evaluates all of its arguments,
and then calls PROCEDURE on the results.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(wrap(args.fst))

@dataclasses.dataclass(frozen=True)
class PrUnwrap(Atomic):
  @property
  def advice(self):
    return f'''
(unwrap PROCEDURE)

If PROCEDURE was created with `wrap` then this procedure will
return its body; if not then an error is raised.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args.fst.to_wrap)

@dataclasses.dataclass(frozen=True)
class PrAdd(Atomic):
  @property
  def advice(self):
    return f'''
(+ NUMBER...)

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
    return go(number(state))

@dataclasses.dataclass(frozen=True)
class PrMul(Atomic):
  @property
  def advice(self):
    return f'''
(* NUMBER...)

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
    return go(number(state))

@dataclasses.dataclass(frozen=True)
class PrSub(Atomic):
  @property
  def advice(self):
    return f'''
(- NUMBER NUMBER...)

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
    return go(number(state))

@dataclasses.dataclass(frozen=True)
class PrDiv(Atomic):
  @property
  def advice(self):
    return f'''
(/ NUMBER NUMBER...)

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
        raise error('Division by zero.')
      else:
        state /= value
      args = args.snd
    return go(number(state))

@dataclasses.dataclass(frozen=True)
class PrAnd(Atomic):
  @property
  def advice(self):
    return f'''
(and CONDITION...)

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
        return go(boolean(True))
      def go_fst(fst):
        if not fst.to_boolean:
          return go(boolean(False))
        return iter(args.snd)
      return eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class PrOr(Atomic):
  @property
  def advice(self):
    return f'''
(or CONDITION...)

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
        return go(boolean(False))
      def go_fst(fst):
        if fst.to_boolean:
          return go(boolean(True))
        return iter(args.snd)
      return eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class PrNot(Atomic):
  @property
  def advice(self):
    return f'''
(not BOOLEAN)

If BOOLEAN is True, return False; if BOOLEAN is False, returns True.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(boolean(not args.fst.to_boolean))

def initial_environment():
  body = {}

  body['print!'] = PrPrint()

  body['True']  = boolean(True)
  body['False'] = boolean(False)

  body['define'] = PrDefine()
  body['let']    = PrLet()
  body['eval']   = PrEval()
  body['vau']    = PrVau()
  body['wrap']   = PrWrap()
  body['unwrap'] = PrUnwrap()

  body['list']  = PrList()
  body['list*'] = PrListStar()
  body['fst']   = PrFst()
  body['snd']   = PrSnd()

  body['+'] = PrAdd()
  body['*'] = PrMul()
  body['-'] = PrSub()
  body['/'] = PrDiv()

  body['and'] = PrAnd()
  body['or']  = PrOr()
  body['not'] = PrNot()

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
        case Atomic():
          # print(proc.advice)
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

def ok(object):
  return Ok(object)

def eval(value, env=None, go=ok):
  if env is None:
    env = initial_environment()
  else:
    env.assert_environment()
  return Eval(value, env, go)

def evlis(value, env=None, go=ok):
  if env is None:
    env = initial_environment()
  else:
    env.assert_environment()
  value.assert_list()
  return Evlis(value, env, go)

def exec(value, env=None, go=None):
  if env is None:
    env = initial_environment()
  else:
    env.assert_environment()
  value.assert_list()
  return Exec(value, env, go)

def apply(proc, args, env=None, go=None):
  if env is None:
    env = initial_environment()
  else:
    env.assert_environment()
  proc.assert_procedure()
  args.assert_list()
  return Apply(proc, args, env, go)

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
      msg = f'Cannot show the unknown object {obj}.'
      raise error(msg)

def norm(initial, env=None, quota=1_000):
  state = eval(initial, env)
  while quota > 0 and not state.is_ok:
    quota -= 1
    state  = step(state)
  state.assert_ok()
  return state.object

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
      object = read(example)[0]
      self.assertEqual(example, f'{object}')

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
      final   = norm(initial)
      self.assertTrue(measure(final))

  def test_nested_operations(self):
    source = '(+ 1 (* 2 3) (- 10 6))'
    initial = read(source)[0]
    final = norm(initial)
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
      final = norm(initial)
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
      final = norm(initial)
      self.assertTrue(measure(final))

  def test_vau_wrap_unwrap(self):
    examples = [
      ['(vau (x) e x)', lambda x: x.is_procedure],
      ['(wrap (vau (x) e x))', lambda x: x.is_procedure and x.is_wrap],
      ['(unwrap (wrap (vau (x) e x)))', lambda x: x.is_procedure and not x.is_wrap],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial)
      self.assertTrue(measure(final))

  def test_miscellaneous_operations(self):
    examples = [
      ['(+ 1 (* 2 3) (- 5 3))', lambda x: x.to_number == 9],
      ['(+ (* 2 (/ 8 4)) (- 10 8))', lambda x: x.to_number == 6],
    ]
    for source, measure in examples:
      initial = read(source)[0]
      final = norm(initial)
      self.assertTrue(measure(final))

  def test_string_escapes(self):
    strings = [
      '"He said \\"Hello, world.\\""',
    ]
    for string in strings:
      object = read(string)[0]
      iterations = random.randint(1, 10)
      for _ in range(iterations):
        object = read(f'{object}')[0]
      #print(f'\nstring={string}\nobject={object}')
      self.assertEqual(f'{object}', string)

if __name__ == '__main__':
  context = initial_environment()
  while True:
    try:
      source  = input('lisp@1.0.0:/\nλ ')
      objects = read(source)
      for object in objects:
        target = norm(object, context)
        print(target)
    except Error as err:
      print(err)

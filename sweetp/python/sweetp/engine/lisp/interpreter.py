from typing import Optional
from typing import Callable
import dataclasses

import sweetp.engine.lisp.value as vx

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

Context = Callable[[vx.Value], State]

@dataclasses.dataclass(frozen=True)
class Ok(State):
  value: vx.Value

  @property
  def is_ok(self):
    return True

  def __str__(self):
    return f'#<ok {self.value}>'

@dataclasses.dataclass(frozen=True)
class Eval(State):
  value: vx.Value
  environment: vx.Value
  ok: Context

  @property
  def is_eval(self):
    return True

  def __str__(self):
    return f'#<eval {self.value}>'

@dataclasses.dataclass(frozen=True)
class Evlis(State):
  value: vx.Value
  environment: vx.Value
  ok: Context

  @property
  def is_evlis(self):
    return True

  def __str__(self):
    return f'#<evlis {self.value}>'

@dataclasses.dataclass(frozen=True)
class Exec(State):
  value: vx.Value
  environment: vx.Value
  ok: Context

  @property
  def is_exec(self):
    return True

  def __str__(self):
    return f'#<exec {self.value}>'

@dataclasses.dataclass(frozen=True)
class Apply(State):
  procedure: vx.Value
  arguments: vx.Value
  environment: vx.Value
  ok: Context

  @property
  def is_apply(self):
    return True

  def __str__(self):
    return f'#<apply {self.value}>'

def ok(value):
  return Ok(value)

def eval(value, env, go=ok):
  env.assert_environment()
  return Eval(value, env, go)

def evlis(value, env, go=ok):
  env.assert_environment()
  value.assert_list()
  return Evlis(value, env, go)

def exec(value, env, go=None):
  env.assert_environment()
  value.assert_list()
  return Exec(value, env, go)

def apply(proc, args, env, go=None):
  env.assert_environment()
  proc.assert_procedure()
  args.assert_list()
  return Apply(proc, args, env, go)

def step(state):
  match state:
    case Ok():
      return state
    case Eval(value, env, go):
      match value:
        case vx.Variable() | vx.Constant():
          if value in env:
            rhs = env[value]
            return go(rhs)
          msg = f'The symbol {value} is undefined.'
          raise error(msg)
        case vx.Pair(proc, args):
          def go_proc(proc):
            return apply(proc, args, env, go)
          return eval(proc, env, go_proc)
        case _:
          return go(value)
    case Evlis(value, env, go):
      match value:
        case vx.Nil():
          return go(value)
        case vx.Pair(fst, snd):
          def go_fst(fst):
            def go_snd(snd):
              return go(vx.pair(fst, snd))
            return evlis(snd, env, go_snd)
          return eval(fst, env, go_fst)
        case _:
          msg = f'Expected a list, but got {value}.'
          raise error(msg)
    case Exec(value, env, go):
      match value:
        case vx.Nil():
          return go(value)
        case vx.Pair(fst, snd):
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
        case vx.Atomic():
          # print(proc.advice)
          if proc.is_applicative:
            def go_args(args):
              try:
                return proc(args, env, go)
              except Error as err:
                raise vx.atomic_error(proc, args, env, err)
            return evlis(args, env, go_args)
          else:
            try:
              return proc(args, env, go)
            except Error as err:
              raise vx.atomic_error(proc, args, env, err)
        case vx.Abstract(head, body, dynamic, lexical):
          try:
            local = vx.environment(next=lexical)
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
          except vx.Error as err:
            raise vx.abstract_error(proc, args, env, err)
        case vx.Wrap(proc):
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

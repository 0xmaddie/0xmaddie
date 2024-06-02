import dataclasses

import sweetp.engine.lisp.value as vx
import sweetp.engine.lisp.interpreter as ix

@dataclasses.dataclass(frozen=True)
class PrPrint(vx.Atomic):
  @property
  def advice(self):
    return f'''
(print VALUE...)

Write the string representation of each VALUE to standard output.
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
    return go(vx.nil())

@dataclasses.dataclass(frozen=True)
class PrList(vx.Atomic):
  @property
  def advice(self):
    return f'''
(list VALUE...)

Return a list containing each VALUE, in order from left to right.
'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    return go(args)

@dataclasses.dataclass(frozen=True)
class PrListStar(vx.Atomic):
  @property
  def advice(self):
    return f'''
(list* VALUE...)

Return a list of the VALUEs, where the last VALUE is the tail of the list.
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
    for value in reversed(buf):
      state = vx.pair(value, state)
    return go(state)

@dataclasses.dataclass(frozen=True)
class PrFst(vx.Atomic):
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
class PrSnd(vx.Atomic):
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
    return go(args.fst.snd)

@dataclasses.dataclass(frozen=True)
class PrDefine(vx.Atomic):
  @property
  def advice(self):
    return f'''
(define NAME VALUE)

Associates NAME with VALUE in the current environment.
'''.strip()

  @property
  def is_applicative(self):
    return False

  def __call__(self, args, env, go):
    lhs = args.fst
    rhs = args.snd.fst
    def go_rhs(rhs):
      env[lhs] = rhs
      return go(vx.nil())
    return ix.eval(rhs, env, go_rhs)

@dataclasses.dataclass(frozen=True)
class PrLet(vx.Atomic):
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
    scope    = vx.environment(next=env)
    def iter(bindings):
      if bindings.is_nil:
        return ix.exec(body, scope, go)
      pair = bindings.fst
      lhs  = pair.fst
      rhs  = pair.snd.fst
      def go_rhs(rhs):
        nonlocal scope
        scope[lhs] = rhs
        return iter(bindings.snd)
      return ix.eval(rhs, scope, go_rhs)
    return iter(bindings)

@dataclasses.dataclass(frozen=True)
class PrEval(vx.Atomic):
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
        return ix.eval(expr, scope, go)
      return ix.eval(scope, env, go_scope)
    else:
      scope = initial_environment()
      return ix.eval(expr, scope, go)

@dataclasses.dataclass(frozen=True)
class PrVau(vx.Atomic):
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
    return go(vx.abstract(head, body, dynamic, lexical))

@dataclasses.dataclass(frozen=True)
class PrWrap(vx.Atomic):
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
    return go(vx.wrap(args.fst))

@dataclasses.dataclass(frozen=True)
class PrUnwrap(vx.Atomic):
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
class PrAdd(vx.Atomic):
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
    return go(vx.number(state))

@dataclasses.dataclass(frozen=True)
class PrMul(vx.Atomic):
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
    return go(vx.number(state))

@dataclasses.dataclass(frozen=True)
class PrSub(vx.Atomic):
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
    return go(vx.number(state))

@dataclasses.dataclass(frozen=True)
class PrDiv(vx.Atomic):
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
    return go(vx.number(state))

@dataclasses.dataclass(frozen=True)
class PrAnd(vx.Atomic):
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
        return go(vx.boolean(True))
      def go_fst(fst):
        if not fst.to_boolean:
          return go(vx.boolean(False))
        return iter(args.snd)
      return ix.eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class PrOr(vx.Atomic):
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
        return go(vx.boolean(False))
      def go_fst(fst):
        if fst.to_boolean:
          return go(vx.boolean(True))
        return iter(args.snd)
      return ix.eval(args.fst, env, go_fst)
    return iter(args)

@dataclasses.dataclass(frozen=True)
class PrNot(vx.Atomic):
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
    return go(vx.boolean(not args.fst.to_boolean))

def initial_environment():
  body = {}

  body['print!'] = PrPrint()

  body['True']  = vx.boolean(True)
  body['False'] = vx.boolean(False)

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

  return vx.environment(body)

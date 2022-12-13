import re
import dataclasses

from typing import Optional
from typing import Union
from typing import List
from typing import Dict
from typing import Generator
from typing import Iterator

def is_valid_constant(token: str) -> bool:
  return re.match(r'^(a|b|c|d|e|f|r|s)$', token) is not None

def is_valid_variable(token: str) -> bool:
  return re.match(r'^[a-z][a-z0-9_]+$', token) is not None

def is_valid_bang(token: str) -> bool:
  return re.match(r'^![a-z][a-z0-9_]+$', token) is not None

def is_separator(token: str) -> bool:
  return token in '[]" \t\r\n'

def is_whitespace(token: str) -> bool:
  return token in ' \t\r\n'

class Error(Exception):
  pass

@dataclasses.dataclass(frozen=True)
class ReadError(Error):
  message: str
  code: Optional[str] = None

  def __str__(self) -> str:
    if self.code:
      return f'error reading `{self.code}`:\n{self.message}'
    else:
      return f'error while reading: {self.message}'

@dataclasses.dataclass(frozen=True)
class EvaluateError(Error):
  code: 'Code'
  message: str

  def __str__(self) -> str:
    return f'error evaluating `{self.code}`:\n{self.message}'

class Token:
  @staticmethod
  def from_string(source: str) -> Iterator['Token']:
    index = 0
    while index < len(source):
      if source[index] == '[':
        yield TBegin()
        index += 1
      elif source[index] == ']':
        yield TEnd()
        index += 1
      elif source[index] == '"':
        index += 1
        start = index
        while index < len(source):
          if source[index] == '"':
            break
          index += 1
        if index >= len(source):
          raise ReadError(f'unbalanced quotes', source)
        body = source[start:index]
        yield TStr(body)
        index += 1
      elif source[index] == '@':
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if is_valid_variable(body[1:]):
          yield TAnn(body)
        else:
          raise ReadError(f'unknown symbol: {body}', source)
      elif source[index] == '!':
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if is_valid_bang(body):
          yield TBang(body)
        else:
          raise ReadError(f'unknown symbol: {body}', source)
      elif source[index].isalpha() and source[index].islower():
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if is_valid_constant(body):
          yield TConst(body)
        elif is_valid_variable(body):
          yield TVar(body)
        else:
          raise ReadError(f'unknown symbol: {body}', source)
      elif source[index].isdigit():
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if body.isdigit():
          yield TNum(int(body))
        else:
          raise ReadError(f'unknown symbol: {body}', source)
      elif source[index] == '+':
        yield TAdd()
        index += 1
      elif source[index] == '-':
        yield TDel()
        index += 1
      elif is_whitespace(source[index]):
        while index < len(source):
          if not is_whitespace(source[index]):
            break
          index += 1
      else:
        raise ReadError(f'unknown token: {source[index]}', source)

  @staticmethod
  def from_code(code: 'Code') -> Iterator['Token']:
    if isinstance(code, Id):
      pass
    elif isinstance(code, Constant):
      yield TConst(code.name)
    elif isinstance(code, Variable):
      yield TVar(code.name)
    elif isinstance(code, Number):
      yield TNum(code.value)
    elif isinstance(code, String):
      yield TStr(code.value)
    elif isinstance(code, Annotation):
      yield TAnn(code.name)
    elif isinstance(code, Bang):
      yield TBang(code.name)
    elif isinstance(code, Quote):
      yield from Token.from_code(code.body)
    elif isinstance(code, DenseSequence):
      for child in code.body:
        yield from Token.from_code(child)
    elif isinstance(code, SparseSequence):
      yield from Token.from_code(code.fst)
      yield from Token.from_code(code.snd)
    else:
      raise ValueError('unreachable')

@dataclasses.dataclass(frozen=True)
class TConst(Token):
  name: str

  def __str__(self) -> str:
    return self.name

@dataclasses.dataclass(frozen=True)
class TVar(Token):
  name: str

  def __str__(self) -> str:
    return self.name

@dataclasses.dataclass(frozen=True)
class TAnn(Token):
  name: str

  def __str__(self) -> str:
    return f'@{self.name}'

@dataclasses.dataclass(frozen=True)
class TBang(Token):
  name: str

  def __str__(self) -> str:
    return f'!{self.name}'

@dataclasses.dataclass(frozen=True)
class TStr(Token):
  value: str

  def __str__(self) -> str:
    return f'"{self.value}"'

@dataclasses.dataclass(frozen=True)
class TNum(Token):
  value: int

  def __str__(self) -> str:
    return f'{self.value}'

@dataclasses.dataclass(frozen=True)
class TBegin(Token):
  def __str__(self) -> str:
    return '['

@dataclasses.dataclass(frozen=True)
class TEnd(Token):
  def __str__(self) -> str:
    return ']'

@dataclasses.dataclass(frozen=True)
class TAdd(Token):
  def __str__(self) -> str:
    return '+'

@dataclasses.dataclass(frozen=True)
class TDel(Token):
  def __str__(self) -> str:
    return '-'

@dataclasses.dataclass(frozen=True)
class TNl(Token):
  def __str__(self) -> str:
    return '\n'

class Code:
  @staticmethod
  def from_string(source: str) -> 'Code':
    return Code.from_tokens(Token.from_string(source))

  @staticmethod
  def from_tokens(tokens: Iterator[Token]) -> 'Code':
    build = []
    stack = []
    done = False
    while not done:
      try:
        token = next(tokens)
        if isinstance(token, TNl):
          done = True
        elif isinstance(token, TBegin):
          stack.append(build)
          build = []
        elif isinstance(token, TEnd):
          if len(stack) == 0:
            raise ReadError(message='unbalanced brackets')
          code = Quote(DenseSequence(build))
          build = stack.pop()
          build.append(code)
        elif isinstance(token, TConst):
          build.append(Constant(token.name))
        elif isinstance(token, TVar):
          build.append(Variable(token.name))
        elif isinstance(token, TNum):
          build.append(Number(token.value))
        elif isinstance(token, TStr):
          build.append(String(token.value))
        elif isinstance(token, TAnn):
          build.append(Annotation(token.name))
        elif isinstance(token, TBang):
          build.append(Bang(token.name))
        else:
          raise ReadError(f'unknown token: {token}')
      except StopIteration:
        done = True
    if len(stack) > 0:
      raise ReadError(message='unbalanced brackets')
    return DenseSequence(build)

@dataclasses.dataclass(frozen=True)
class Id(Code):
  def __str__(self) -> str:
    return ''

@dataclasses.dataclass(frozen=True)
class Constant(Code):
  name: str

  def __str__(self) -> str:
    return self.name

@dataclasses.dataclass(frozen=True)
class Variable(Code):
  name: str

  def __str__(self) -> str:
    return self.name

@dataclasses.dataclass(frozen=True)
class Annotation(Code):
  name: str

  def __str__(self):
    return self.name

@dataclasses.dataclass(frozen=True)
class Bang(Code):
  name: str

  def __str__(self):
    return self.name

@dataclasses.dataclass(frozen=True)
class SparseSequence(Code):
  fst: Code
  snd: Code

  def __str__(self) -> str:
    return f'{self.fst} {self.snd}'

@dataclasses.dataclass(frozen=True)
class DenseSequence(Code):
  body: list[Code]

  def __str__(self) -> str:
    body = [f'{child}' for child in self.body]
    return ' '.join(body)

@dataclasses.dataclass(frozen=True)
class Quote(Code):
  body: Code

  def __str__(self) -> str:
    return f'[{self.body}]'

@dataclasses.dataclass(frozen=True)
class String(Code):
  value: str

  def __str__(self) -> str:
    return f'"{self.value}"'

@dataclasses.dataclass(frozen=True)
class Number(Code):
  value: int

  def __str__(self) -> str:
    return f'{self.value}'

class State:
  todo: List[Code]
  data: List[Code]
  kill: List[Code]
  point: Optional[Code]

  def __init__(self, code: Code):
    self.todo = [code]
    self.data = []
    self.kill = []
    self.point = None

  @property
  def is_done(self) -> bool:
    return len(self.todo) == 0

  @property
  def is_empty(self) -> bool:
    return len(self.data) == 0

  @property
  def arity(self) -> int:
    return len(self.data)

  @property
  def as_code(self) -> Code:
    buf = self.kill+self.data
    if self.point is not None:
      buf.append(self.point)
    buf.extend(reversed(self.todo))
    return DenseSequence(buf)

  def next(self) -> Code:
    self.point = self.todo.pop()
    return self.point

  def schedule(self, code: Code):
    if isinstance(code, SparseSequence):
      self.todo.append(code.snd)
      self.todo.append(code.fst)
    elif isinstance(code, DenseSequence):
      self.todo.extend(reversed(code.body))
    else:
      self.todo.append(code)

  def jump(self) -> Optional[Code]:
    has_reset = False
    buf = []
    while len(self.todo) > 0 and not has_reset:
      code = self.todo.pop()
      if isinstance(code, Constant):
        if code.name == 'r':
          has_reset = True
        else:
          buf.append(code)
      elif isinstance(code, SparseSequence):
        self.schedule(code)
      elif isinstance(code, DenseSequence):
        self.schedule(code)
      else:
        buf.append(code)
    if not has_reset:
      assert len(self.todo) == 0
      self.todo = buf
      return None
    else:
      continuation = DenseSequence(buf)
      continuation = Quote(continuation)
      return continuation

  def push(self, code: Code):
    self.data.append(code)

  def pop(self) -> Code:
    return self.data.pop()

  def peek(self, index: int = 0) -> Code:
    return self.data[-1-index]

  def thunk(self):
    assert self.point is not None
    self.kill.extend(self.data)
    self.kill.append(self.point)
    self.data = []
    self.point = None

  def bail(self):
    self.thunk()
    self.kill.extend(self.todo)
    self.todo = []

class Event:
  pass

@dataclasses.dataclass(frozen=True)
class EVar(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class EAnn(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class EBang(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class EDone(Event):
  state: State

class Evaluator:
  def __call__(self, init: Code) -> Iterator[Event]:
    state = State(init)

    while not state.is_done:
      code = state.next()
      if isinstance(code, Id):
        pass
      elif isinstance(code, DenseSequence):
        state.schedule(code)
      elif isinstance(code, SparseSequence):
        state.schedule(code)
      elif isinstance(code, Quote):
        state.push(code)
      elif isinstance(code, String):
        state.push(code)
      elif isinstance(code, Number):
        state.push(code)
      elif isinstance(code, Variable):
        yield EVar(state)
      elif isinstance(code, Annotation):
        yield EAnn(state)
      elif isinstance(code, Bang):
        yield EBang(state)
      elif isinstance(code, Constant):
        if code.name == 'a':
          if state.is_empty:
            state.thunk()
          else:
            block = state.peek()
            if not isinstance(block, Quote):
              state.thunk()
            else:
              state.pop()
              state.schedule(block.body)
        elif code.name == 'b':
          if state.is_empty:
            state.thunk()
          else:
            value = state.pop()
            value = Quote(value)
            state.push(value)
        elif code.name == 'c':
          if state.arity < 2:
            state.thunk()
          else:
            lhs = state.peek(1)
            rhs = state.peek(0)
            if not isinstance(lhs, Quote) or not isinstance(rhs, Quote):
              state.thunk()
            else:
              state.pop()
              state.pop()
              block = SparseSequence(lhs.body, rhs.body)
              block = Quote(block)
              state.push(block)
        elif code.name == 'd':
          if state.is_empty:
            state.thunk()
          else:
            value = state.peek()
            state.push(value)
        elif code.name == 'e':
          if state.is_empty:
            state.thunk()
          else:
            state.pop()
        elif code.name == 'f':
          if state.arity < 2:
            state.thunk()
          else:
            fst = state.pop()
            snd = state.pop()
            state.push(fst)
            state.push(snd)
        elif code.name == 'r':
          state.thunk()
        elif code.name == 's':
          if state.is_empty:
            state.bail()
          else:
            value = state.peek()
            if not isinstance(value, Quote):
              state.bail()
            else:
              context = state.jump()
              if context is None:
                state.bail()
              else:
                state.pop()
                state.push(context)
                state.schedule(value.body)
        else:
          raise EvaluateError(init, f'unknown code: {code}')
      else:
        raise EvaluateError(init, f'unknown code: {code}')

    state.point = None
    yield EDone(state)

class Command:
  @staticmethod
  def from_string(source: str) -> 'Command':
    return Command.from_tokens(Token.from_string(source))

  @staticmethod
  def from_tokens(tokens: Iterator[Token]) -> 'Command':
    prefix = next(tokens)
    if isinstance(prefix, TAdd):
      maybe_var = next(tokens)
      if not isinstance(maybe_var, TVar):
        msg = ''
        msg += 'while reading an ADD command,\n'
        msg += 'encountered an unexpected symbol: '
        msg += f'{maybe_var}'
        raise ReadError(msg)
      key = Variable(maybe_var.name)
      value = Code.from_tokens(tokens)
      return CAdd(key, value)
    elif isinstance(prefix, TDel):
      maybe_var = next(tokens)
      if not isinstance(maybe_var, TVar):
        msg = ''
        msg += 'while reading a DEL command,\n'
        msg += 'encountered an unexpected symbol: '
        msg += f'{maybe_var}'
        raise ReadError(msg)
      key = Variable(maybe_var.name)
      return CDel(key)
    else:
      def iterator():
        yield prefix
        yield from tokens
      value = Code.from_tokens(iterator())
      return CEval(value)

@dataclasses.dataclass(frozen=True)
class CAdd(Command):
  key: Variable
  value: Code

  def __str__(self) -> str:
    return f'+{self.key} {self.value}'

@dataclasses.dataclass(frozen=True)
class CDel(Command):
  key: Variable

  def __str__(self) -> str:
    return f'-{self.key}'

@dataclasses.dataclass(frozen=True)
class CEval(Command):
  value: Code

  def __str__(self) -> str:
    return f'{self.value}'

class Database:
  value: Dict[str, Code]

  def __init__(self):
    self.value = {}

  def __contains__(
    self,
    key: str | Variable,
  ) -> bool:
    if isinstance(key, str):
      return key in self.value
    return key.name in self.value

  def __getitem__(
    self,
    key: str | Variable,
  ) -> Code:
    if isinstance(key, str):
      return self.value[key]
    return self.value[key.name]

  def __setitem__(
    self,
    key: str | Variable,
    value: Code,
  ):
    if isinstance(key, str):
      self.value[key] = value
    else:
      self.value[key.name] = value

  def __delitem__(
    self,
    key: str | Variable,
  ):
    if isinstance(key, str):
      if key in self.value:
        del self.value[key]
    else:
      if key.name in self.value:
        del self.value[key.name]

  def __str__(self) -> str:
    buf = [f'+{key} {value}' for key, value in self.value]
    return '\n'.join(buf)

def shell():
  db = Database()
  eval = Evaluator()
  done = False
  while not done:
    try:
      line = input('abc> ').strip()
      cmd = Command.from_string(line)
      if isinstance(cmd, CAdd):
        db[cmd.key] = cmd.value
        print(cmd)
      elif isinstance(cmd, CDel):
        del db[cmd.key]
        print(cmd)
      elif isinstance(cmd, CEval):
        for event in eval(cmd.value):
          if isinstance(event, EDone):
            print(event.state.as_code)
          elif isinstance(event, EVar):
            key = event.state.point
            assert isinstance(key, Variable)
            if key in db:
              binding = db[key]
              event.state.push(binding)
            else:
              event.state.thunk()
          elif isinstance(event, EBang):
            event.state.thunk()
          elif isinstance(event, EAnn):
            pass
      else:
        raise ValueError(f'unknown command: {cmd}')
    except ReadError as err:
      print(err)
    except KeyboardInterrupt:
      done = True
  print('\nbye')

if __name__ == '__main__':
  examples = [
    ['[foo] a', 'foo'],
    ['[foo] b', '[[foo]]'],
    ['[foo] [bar] c', '[foo bar]'],
    ['[foo] d', '[foo] [foo]'],
    ['[foo] e', ''],
    ['[foo] [bar] f', '[bar] [foo]'],
    ['[foo] s bar baz qux r', '[bar baz qux] foo'],

    ['[foo] a [bar] a', 'foo bar'],
    ['[foo] b b', '[[[foo]]]'],
    ['[foo] [bar] c [qux] c', '[foo bar qux]'],
    ['[foo] d d', '[foo] [foo] [foo]'],
    ['[foo] [bar] e e', ''],
    ['[foo] [bar] f f', '[foo] [bar]'],
    ['[foo] s bar baz qux', '[foo] s bar baz qux'],
    ['500 d', '500 500'],
    ['"an oil painting" d', '"an oil painting" "an oil painting"'],
  ]

  eval = Evaluator()

  for [source, expected] in examples:
    code = Code.from_string(source)
    for event in eval(code):
      if isinstance(event, EDone):
        actual = f'{event.state.as_code}'
        assert actual == expected
        print(f'{source} -> {actual}')
      elif isinstance(event, EVar):
        event.state.thunk()
      elif isinstance(event, EAnn):
        pass
      elif isinstance(event, EBang):
        event.state.thunk()

  # repl()
  shell()

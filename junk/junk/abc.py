import re
import dataclasses

from typing import Optional
from typing import List
from typing import Dict
from typing import Generator

def is_valid_constant(token: str) -> bool:
  return re.match(r'^(a|b|c|d|e|f|r|s)$', token) is not None

def is_valid_variable(token: str) -> bool:
  return re.match(r'^[a-z][a-z0-9_]+$', token) is not None

def is_valid_command(token: str) -> bool:
  return re.match(r'^![a-z][a-z0-9_]+$', token) is not None

def is_separator(token: str) -> bool:
  return token in '[]" \t\r\n'

def is_whitespace(token: str) -> bool:
  return token in ' \t\r\n'

class Error(Exception):
  pass

@dataclasses.dataclass(frozen=True)
class ReadError(Error):
  code: str
  message: str

  def __str__(self) -> str:
    return f'error reading `{self.code}`:\n{self.message}'

@dataclasses.dataclass(frozen=True)
class EvaluateError(Error):
  code: 'Code'
  message: str

  def __str__(self) -> str:
    return f'error evaluating `{self.code}`:\n{self.message}'

class Code:
  @staticmethod
  def from_string(source: str) -> 'Code':
    index = 0
    build = []
    stack = []
    while index < len(source):
      if source[index] == '[':
        stack.append(build)
        build = []
        index += 1
      elif source[index] == ']':
        if len(stack) == 0:
          raise ReadError(source, f'unbalanced brackets')
        code = DenseSequence(build)
        code = Quote(code)
        build = stack.pop()
        build.append(code)
        index += 1
      elif source[index] == '"':
        index += 1
        start = index
        while index < len(source):
          if source[index] == '"':
            break
          index += 1
        if index >= len(source):
          raise ReadError(source, f'unbalanced quotes')
        body = source[start:index]
        code = String(body)
        build.append(code)
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
          code = Annotation(body)
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif source[index] == '!':
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if is_valid_command(body):
          code = Command(body)
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif source[index].isalpha() and source[index].islower():
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if is_valid_constant(body):
          code = Constant(body)
          build.append(code)
        elif is_valid_variable(body):
          code = Variable(body)
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif source[index].isdigit():
        start = index
        index += 1
        while index < len(source):
          if is_separator(source[index]):
            break
          index += 1
        body = source[start:index]
        if body.isdigit():
          code = Natural(int(body))
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif is_whitespace(source[index]):
        while index < len(source):
          if not is_whitespace(source[index]):
            break
          index += 1
      else:
        raise ReadError(source, f'unknown token: {source[index]}')
    if len(stack) > 0:
      raise ReadError(source, f'unbalanced brackets')
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
class Command(Code):
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
class Natural(Code):
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
class OnVariable(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class OnAnnotation(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class OnCommand(Event):
  state: State

@dataclasses.dataclass(frozen=True)
class OnResult(Event):
  state: State

class Evaluate:
  def __call__(self, init: Code) -> Generator[Event, None, None]:
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
      elif isinstance(code, Natural):
        state.push(code)
      elif isinstance(code, Variable):
        yield OnVariable(state)
      elif isinstance(code, Annotation):
        yield OnAnnotation(state)
      elif isinstance(code, Command):
        yield OnCommand(state)
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
    yield OnResult(state)

class Database:
  value: Dict[str, Code]

  def __init__(self):
    self.value = {}

  def __contains__(self, key: str) -> bool:
    return key in self.value

  def __getitem__(self, key: str) -> Code:
    return self.value[key]

  def __setitem__(self, key: str, value: Code):
    self.value[key] = value

  def __delitem__(self, key: str):
    if key in self.value:
      del self.value[key]

  def __str__(self) -> str:
    buf = [f'+{key} {value}' for key, value in self.value]
    return '\n'.join(buf)

def repl():
  db = Database()
  eval = Evaluate()
  while True:
    line = input('abc> ').strip()
    if line == '/quit':
      break
    try:
      if line.startswith('+'):
        chunks = line[1:].split(' ', maxsplit=1)
        if len(chunks) == 2:
          name, body = chunks
          if not is_valid_variable(name):
            print(f'invalid word: {name}')
          else:
            code = Code.from_string(body)
            db[name] = code
            print(f'{name} = {code}')
        else:
          name = chunks[0]
          if not is_valid_variable(name):
            print(f'invalid word: {name}')
          else:
            print(f'{name} = {name}')
      elif line.startswith('-'):
        name = line[1:].strip()
        if not is_valid_variable(name):
          print(f'invalid word: {name}')
        if name in db:
          del db[name]
        print(f'{name} = {name}')
      else:
        code = Code.from_string(line)
        for event in eval(code):
          if isinstance(event, OnResult):
            print(event.state.as_code)
          elif isinstance(event, OnVariable):
            point = event.state.point
            if isinstance(point, Variable) and point.name in db:
              binding = db[point.name]
              event.state.schedule(binding)
            else:
              event.state.thunk()
          elif isinstance(event, OnAnnotation):
            pass
          elif isinstance(event, OnCommand):
            event.state.thunk()
    except Error as err:
      print(err)

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

  eval = Evaluate()

  for [source, expected] in examples:
    code = Code.from_string(source)
    for event in eval(code):
      if isinstance(event, OnResult):
        actual = f'{event.state.as_code}'
        assert actual == expected
        print(f'{source} -> {actual}')
      elif isinstance(event, OnVariable):
        event.state.thunk()
      elif isinstance(event, OnAnnotation):
        pass
      elif isinstance(event, OnCommand):
        event.state.thunk()

  repl()

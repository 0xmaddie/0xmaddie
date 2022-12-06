import re
import dataclasses

from typing import Dict
from typing import Optional

def is_valid_constant(token: str) -> bool:
  return re.match('^(a|b|c|d|e|f|r|s)$', token)

def is_valid_variable(token: str) -> bool:
  return re.match('^[a-z][a-z0-9-]+$', token)

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
      elif source[index].startswith('@'):
        index += 1
        start = index
        while index < len(source):
          if source[index] in '[]" ':
            break
          index += 1
        body = source[start:index]
        if is_valid_variable(body):
          code = Annotation(body)
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif source[index].isalpha() and source[index].islower():
        start = index
        index += 1
        while index < len(source):
          if source[index] in '[]" ':
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
          if source[index] in '[]" ':
            break
          index += 1
        body = source[start:index]
        if body.isdigit():
          code = Natural(int(body))
          build.append(code)
        else:
          raise ReadError(source, f'unknown symbol: {body}')
      elif source[index] in ' \t\r\n':
        while index < len(source):
          if source[index] not in ' \t\r\n':
            break
          index += 1
      else:
        raise ReadError(source, f'unknown token: {source[index]}')
    if len(stack) > 0:
      raise ReadError(f'unbalanced brackets')
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

class Evaluate:
  def __call__(self, code: Code) -> Code:
    todo = [code]
    data = []
    kill = []

    def thunk():
      nonlocal data
      kill.extend(data)
      kill.append(code)
      data = []

    def bail():
      nonlocal todo
      nonlocal data
      kill.extend(data)
      kill.append(code)
      kill.extend(todo)
      data = []
      todo = []

    while len(todo) > 0:
      code = todo.pop()
      if isinstance(code, DenseSequence):
        todo.extend(reversed(code.body))
      elif isinstance(code, SparseSequence):
        todo.append(code.fst)
        todo.append(code.snd)
      elif isinstance(code, Quote):
        data.append(code)
      elif isinstance(code, String):
        data.append(code)
      elif isinstance(code, Natural):
        data.append(code)
      elif isinstance(code, Variable):
        thunk()
      elif isinstance(code, Id):
        pass
      elif isinstance(code, Annotation):
        pass
      elif isinstance(code, Constant):
        if code.name == 'a':
          if len(data) == 0:
            thunk()
          else:
            block = data[-1]
            if not isinstance(block, Quote):
              thunk()
            else:
              data.pop()
              todo.append(block.body)
        elif code.name == 'b':
          if len(data) == 0:
            thunk()
          else:
            value = data.pop()
            value = Quote(value)
            data.append(value)
        elif code.name == 'c':
          if len(data) < 2:
            thunk()
          else:
            lhs = data[-2]
            rhs = data[-1]
            if not isinstance(lhs, Quote) or not isinstance(rhs, Quote):
              thunk()
            else:
              data.pop()
              data.pop()
              block = SparseSequence(lhs.body, rhs.body)
              block = Quote(block)
              data.append(block)
        elif code.name == 'd':
          if len(data) == 0:
            thunk()
          else:
            value = data[-1]
            data.append(value)
        elif code.name == 'e':
          if len(data) == 0:
            thunk()
          else:
            data.pop()
        elif code.name == 'f':
          if len(data) < 2:
            thunk()
          else:
            fst = data.pop()
            snd = data.pop()
            data.append(fst)
            data.append(snd)
        elif code.name == 'r':
          thunk()
        elif code.name == 's':
          if len(data) == 0:
            bail()
          else:
            value = data[-1]
            if not isinstance(value, Quote):
              bail()
            else:
              has_reset = False
              buf = []
              while len(todo) > 0 and not has_reset:
                point = todo.pop()
                if isinstance(point, Constant):
                  if point.name == 'r':
                    has_reset = True
                  else:
                    buf.append(point)
                elif isinstance(point, SparseSequence):
                  todo.append(point.snd)
                  todo.append(point.fst)
                elif isinstance(point, DenseSequence):
                  todo.extend(reversed(point.body))
                else:
                  buf.append(point)
              if not has_reset:
                assert len(todo) == 0
                bail()
                kill.extend(buf)
              else:
                data.pop()
                continuation = DenseSequence(buf)
                continuation = Quote(continuation)
                data.append(continuation)
                todo.append(value.body)
        else:
          raise ValueError(f'unknown code: {code}')
      else:
        raise ValueError(f'unknown code: {code}')

    return DenseSequence(kill+data)

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

def repl():
  db = Database()
  eval = Evaluate()
  while True:
    line = input('abc> ')
    if line == '__quit__':
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
        code = eval(code)
        print(code)
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
    ['"by john singer sargent" d', '"by john singer sargent" "by john singer sargent"'],
  ]

  eval = Evaluate()

  for [source, expected] in examples:
    code = Code.from_string(source)
    code = eval(code)
    actual = f'{code}'
    # print(f'{source} ?-> {actual} (expected {expected})')
    assert actual == expected
    print(f'{source} -> {actual}')

  repl()

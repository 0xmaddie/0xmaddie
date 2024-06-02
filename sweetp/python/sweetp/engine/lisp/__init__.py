from sweetp.engine.lisp.value import Value
from sweetp.engine.lisp.value import Nil
from sweetp.engine.lisp.value import Pair
from sweetp.engine.lisp.value import Constant
from sweetp.engine.lisp.value import Variable
from sweetp.engine.lisp.value import Boolean
from sweetp.engine.lisp.value import Number
from sweetp.engine.lisp.value import String
from sweetp.engine.lisp.value import Keyword
from sweetp.engine.lisp.value import Environment
from sweetp.engine.lisp.value import Atomic
from sweetp.engine.lisp.value import Abstract
from sweetp.engine.lisp.value import Wrap
from sweetp.engine.lisp.value import Error
from sweetp.engine.lisp.value import nil
from sweetp.engine.lisp.value import pair
from sweetp.engine.lisp.value import list
from sweetp.engine.lisp.value import constant
from sweetp.engine.lisp.value import variable
from sweetp.engine.lisp.value import keyword
from sweetp.engine.lisp.value import boolean
from sweetp.engine.lisp.value import number
from sweetp.engine.lisp.value import string
from sweetp.engine.lisp.value import environment
from sweetp.engine.lisp.value import atomic
from sweetp.engine.lisp.value import abstract
from sweetp.engine.lisp.value import wrap
from sweetp.engine.lisp.value import from_list
from sweetp.engine.lisp.value import from_dict
from sweetp.engine.lisp.value import read

from sweetp.engine.lisp.interpreter import State
from sweetp.engine.lisp.interpreter import Context
from sweetp.engine.lisp.interpreter import Ok
from sweetp.engine.lisp.interpreter import Eval
from sweetp.engine.lisp.interpreter import Evlis
from sweetp.engine.lisp.interpreter import Exec
from sweetp.engine.lisp.interpreter import Apply
from sweetp.engine.lisp.interpreter import ok
from sweetp.engine.lisp.interpreter import eval
from sweetp.engine.lisp.interpreter import evlis
from sweetp.engine.lisp.interpreter import exec
from sweetp.engine.lisp.interpreter import apply
from sweetp.engine.lisp.interpreter import step
from sweetp.engine.lisp.interpreter import norm

from sweetp.engine.lisp.procedure import initial_environment

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

if __name__ == '__main__':
  context = initial_environment()
  while True:
    try:
      source  = input('lisp@1.0.0:/\nλ ')
      values = read(source)
      for value in values:
        target = norm(value, context)
        print(target)
    except Error as err:
      print(err)

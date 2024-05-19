import studio.lisp as lisp
import google.generativeai as gemini

class GeminiCompleteString(lisp.Extension):
  model: gemini.GenerativeModel

  @property
  def advice(self):
    return f'''

'''.strip()

  @property
  def is_applicative(self):
    return True

  def __call__(self, args, env, go):
    string   = args.fst.to_string
    response = self.model.generate_content(string)
    target   = lisp.string(response.text)
    return go(target)

class BuildPackage:
  def __call__(self):
    pass

def get_lisp_package(google_api_key):
  gemini.configure(api_key=google_api_key)
  model = gemini.GenerativeModel('gemini-1.5-flash')
  env   = {}

  def define(name, body):
    nonlocal env
    env[f'gemini.{name}'] = body(model)

  define('complete', GeminiCompleteString)

  return env

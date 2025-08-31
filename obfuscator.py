import random
import string
import ast
import astor
import builtins
import keyword
import re

builtins_set = set(dir(builtins)) | set(keyword.kwlist)


def generate_unique_name(used_names, length=6):
    while True:
        name = random.choice(string.ascii_letters) + ''.join(
            random.choices(string.ascii_letters + string.digits, k=length - 1))
        if name not in used_names:
            used_names.add(name)
            return name


class Obfuscator(ast.NodeTransformer):
    def __init__(self):
        self.nameMap = {}
        self.used_names = set()

    def randomName(self, length=6):
        return generate_unique_name(self.used_names, length)

    def newName(self, name):
        if name in builtins_set or name.startswith(""):
            return name
        if name not in self.nameMap:
            self.nameMap[name] = self.randomName()
        return self.nameMap.get(name, name)

    def visit_FunctionDef(self, node):
        node.name = self.newName(node.name)
        self.generic_visit(node)
        return node

    def visit_arg(self, node):
        node.arg = self.newName(node.arg)
        return node

    def visit_Name(self, node):
        node.id = self.newName(node.id)
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            random_value = ''.join(random.choices(string.ascii_letters + string.digits, k=len(node.value)))
            return ast.Constant(value=random_value)
        return node

def Obfuscator_Code(code):
    obfuscator = Obfuscator()
    tree = obfuscator.visit(ast.parse(code))
    obfuscated = astor.to_source(tree)
    return obfuscated, obfuscator

def builtin_Obfuscate(code, used_names):
    byte_code = compile(code, "<string>", "exec")
    builtin_used = [name for name in byte_code.co_names if name in builtins_set]
    rename_map = {name: generate_unique_name(used_names) for name in builtin_used}

    for orig, obf in rename_map.items():
        code = re.sub(rf'(?<!\.)\b{re.escape(orig)}\b', obf, code)

    stub_lines = [f'{obf} = getattr(_builtins_, "{orig}")' for orig, obf in rename_map.items()]
    stub_code = "\n".join(stub_lines)
    final_code = stub_code + "\n\n" + code
    return final_code

def spaceRemove(code):
    return re.sub(r'#.*', '', code)

def Obfuscator_path(input_path, output_file):
    with open(input_path, 'r') as file:
        code = file.read()

    obfuscated_code, obfuscator = Obfuscator_Code(code)
    final_code = builtin_Obfuscate(obfuscated_code, obfuscator.used_names)
    final_code = spaceRemove(final_code)

    with open(output_file, 'w') as f:
        f.write(final_code)
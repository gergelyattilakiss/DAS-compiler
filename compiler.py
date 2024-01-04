import re

TOKEN_TYPES = [
        ['def', r'\bdef\b'],
        ['identifier', r'\b[a-zA-Z]+\b'],
        ['integer', r'\b[0-9]+\b'],
        ['colon', r':'],
        ['oparent', r'\('],
        ['cparent', r'\)'],
        ['comma', r','], 
]

class Tokeinzer:
    def __init__(self, code) -> None:
        self.code = code

    def tokenize(self):
        self.tokens = []
        while self.code:
            self.tokens.append(self.tokenize_one_token())
            self.code = self.code.strip()
        return self.tokens

    def tokenize_one_token(self):
        for t,regex in TOKEN_TYPES:
            p = re.compile(rf'\A({regex})')
            m = p.match(self.code)
            if m:
                value = m.group()
                self.code = self.code[len(value):]
                return Token(t, value)

class Token:
    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value

class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens

    def parse(self):
        return self.parse_def()
    
    def parse_def(self):
        self.consume('def')
        name = self.consume('identifier')
        arg_names = self.parse_arg_names()
        body = self.parse_expr()
        return DefNode(name, arg_names, body)

    def consume(self, expected_type):
        token = self.tokens.pop(0)
        if token.type == expected_type:
            return token.value
        else:
            raise RuntimeError(f"Expected token type {expected_type} but got {token.type}.")
        
    def parse_arg_names(self):
        arg_names = []
        self.consume('oparent')
        if self.peek('identifier'):
            arg_names.append(self.consume('identifier'))
            while self.peek('comma'):
                self.consume('comma')
                arg_names.append(self.consume('identifier'))
        self.consume('cparent')
        self.consume('colon')
        return arg_names

    def parse_expr(self):
        if self.peek('integer'):
            return self.parse_integer()
        if self.peek('identifier') and self.peek('oparent', 1):
            return self.parse_call()
        return self.parse_var_ref()

    def parse_integer(self):
        return IntegerNode(int(self.consume('integer'))).value
    
    def parse_call(self):
        name = self.consume('identifier')
        arg_exprs = self.parse_arg_exprs()
        return CallNode(name, arg_exprs)
    
    def parse_var_ref(self):
        return VarRefNode(self.consume('identifier'))
    
    def parse_arg_exprs(self):
        arg_exprs = []
        self.consume('oparent')
        if self.peek('cparent') != True: 
            arg_exprs.append(self.parse_expr())
            while self.peek('cparent') != True:
                self.consume('comma')
                arg_exprs.append(self.parse_expr())
        self.consume('cparent')
        return arg_exprs

    def peek(self, expected_type, offset=0):
        return self.tokens[offset].type == expected_type

class DefNode:
    def __init__(self, name , arg_names, body) -> None:
        self.name = name
        self.arg_names = arg_names
        self.body = body

class IntegerNode:
    def __init__(self, value) -> None:
        self.value = value

class CallNode:
    def __init__(self, name, arg_exprs) -> None:
        self.name = name
        self.arg_exprs = arg_exprs

class VarRefNode:
    def __init__(self, value) -> None:
        self.value = value

class Generator:
    def __init__(self) -> None:
        pass

    def generate(self, node):
        if isinstance(node, DefNode):
            return "function %s(%s) {return %s};" % (
                node.name, 
                ','.join(node.arg_names), 
                self.generate(node.body))
        
        if isinstance(node, CallNode):
            return "%s(%s)" % (
                node.name, 
                ','.join([self.generate(expr) for expr in node.arg_exprs])
                )
        
        if isinstance(node, int):
            return str(node)

        if isinstance(node, VarRefNode):
            return node.value
        
        raise RuntimeError(f"Unexpected node type: {node.__class__}")


tokens = Tokeinzer(open("test.src").read()).tokenize()
tree = Parser(tokens).parse()
generator = Generator()
generated = generator.generate(tree)
print(generated)
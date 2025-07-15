import unittest
from lexer import Lexer
from parser import Parser
from minilang_ast import *

class TestParser(unittest.TestCase):
    def test_function_and_vardecl(self):
        code = 'int main() { int x = 5; return x; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, Program)
        self.assertIsInstance(ast.functions[0], FunctionDef)
        self.assertIsInstance(ast.functions[0].body.statements[0], VariableDecl)

    def test_if_else_and_while(self):
        code = 'int f() { if (1 == 1) { return 1; } else { return 0; } while (0) { x = 1; } }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmts = ast.functions[0].body.statements
        self.assertTrue(any(isinstance(s, If) for s in stmts))
        self.assertTrue(any(isinstance(s, While) for s in stmts))

    def test_expression(self):
        code = 'int f() { int x = 1 + 2 * 3; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        vardecl = ast.functions[0].body.statements[0]
        self.assertIsInstance(vardecl.initializer, BinaryOp)

if __name__ == '__main__':
    unittest.main() 
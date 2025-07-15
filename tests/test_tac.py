import unittest
from lexer import Lexer
from parser import Parser
from tac import TACGenerator, TACInstruction

class TestTACGenerator(unittest.TestCase):
    def test_assignment_and_arithmetic(self):
        code = 'int main() { int x = 1 + 2; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        tacgen = TACGenerator()
        tac = tacgen.generate(ast)
        self.assertTrue(any(instr.op == '+' for instr in tac))
        self.assertTrue(any(instr.op == '=' for instr in tac))

    def test_if_else(self):
        code = 'int main() { if (1) { x = 1; } else { x = 2; } }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        tacgen = TACGenerator()
        tac = tacgen.generate(ast)
        self.assertTrue(any(instr.op == 'ifz' for instr in tac))
        self.assertTrue(any(instr.op == 'goto' for instr in tac))

    def test_while(self):
        code = 'int main() { while (1) { x = 1; } }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        tacgen = TACGenerator()
        tac = tacgen.generate(ast)
        self.assertTrue(any(instr.op == 'ifz' for instr in tac))
        self.assertTrue(any(instr.op == 'goto' for instr in tac))

    def test_function_call(self):
        code = 'int foo(int a) { return a; } int main() { int x = foo(1); }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        tacgen = TACGenerator()
        tac = tacgen.generate(ast)
        self.assertTrue(any(instr.op == 'call' for instr in tac))

if __name__ == '__main__':
    unittest.main() 
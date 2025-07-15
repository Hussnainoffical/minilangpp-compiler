import unittest
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer

class TestSemanticAnalyzer(unittest.TestCase):
    def test_undeclared_variable(self):
        code = 'int main() { x = 5; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertTrue(any('Undeclared variable' in e for e in analyzer.errors))

    def test_type_mismatch(self):
        code = 'int main() { int x = 5.5; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertTrue(any('Type mismatch' in e for e in analyzer.errors))

    def test_function_call_error(self):
        code = 'int main() { foo(1); }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertTrue(any('Undeclared function' in e for e in analyzer.errors))

    def test_symbol_table(self):
        code = 'int main() { int x = 1; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        # Should have at least global and function scopes
        self.assertGreaterEqual(len(analyzer.symbol_stack.stack), 1)

if __name__ == '__main__':
    unittest.main() 
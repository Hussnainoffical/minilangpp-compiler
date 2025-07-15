import unittest
from lexer import Lexer

class TestLexer(unittest.TestCase):
    def test_keywords_and_identifiers(self):
        code = 'int x = 5; float y = 2.5; bool flag = true;'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        self.assertIn('INT', types)
        self.assertIn('FLOAT', types)
        self.assertIn('BOOL', types)
        self.assertIn('ID', types)
        self.assertIn('INT_LIT', types)
        self.assertIn('FLOAT_LIT', types)
        self.assertIn('TRUE', types)
        self.assertIn('SEMI', types)

    def test_operators_and_delimiters(self):
        code = 'x = y + 2 * (z - 1);'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        self.assertIn('ASSIGN', types)
        self.assertIn('PLUS', types)
        self.assertIn('MUL', types)
        self.assertIn('LPAREN', types)
        self.assertIn('RPAREN', types)
        self.assertIn('MINUS', types)

    def test_invalid_token(self):
        code = 'int $x = 5;'
        lexer = Lexer(code)
        lexer.tokenize()
        self.assertTrue(any('Invalid token' in err for err in lexer.errors))

if __name__ == '__main__':
    unittest.main() 
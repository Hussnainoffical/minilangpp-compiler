import re
from typing import List, Tuple, Optional

# Token specification for MiniLang++
TOKEN_SPECIFICATION = [
    ('INT',        r'int\b'),
    ('FLOAT',      r'float\b'),
    ('BOOL',       r'bool\b'),
    ('IF',         r'if\b'),
    ('ELSE',       r'else\b'),
    ('WHILE',      r'while\b'),
    ('RETURN',     r'return\b'),
    ('TRUE',       r'true\b'),
    ('FALSE',      r'false\b'),
    # Multi-character operators first!
    ('EQ',         r'=='),
    ('NEQ',        r'!='),
    ('LE',         r'<='),
    ('GE',         r'>='),
    ('AND',        r'&&'),
    ('OR',         r'\|\|'),
    # Single-character operators
    ('ASSIGN',     r'='),
    ('LT',         r'<'),
    ('GT',         r'>'),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('MUL',        r'\*'),
    ('DIV',        r'/'),
    ('NOT',        r'!'),
    # Delimiters
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('COMMA',      r','),
    ('SEMI',       r';'),
    # Literals
    ('FLOAT_LIT',  r'\d+\.\d+'),
    ('INT_LIT',    r'\d+'),
    # Identifiers
    ('ID',         r'[A-Za-z_][A-Za-z0-9_]*'),
    # Whitespace and newlines
    ('SKIP',       r'[ \t]+'),
    ('NEWLINE',    r'\n'),
    # Anything else
    ('MISMATCH',   r'.'),
]

# Compile regex
TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
get_token = re.compile(TOK_REGEX).match

class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Token] = []
        self.errors: List[str] = []

    def tokenize(self) -> List[Token]:
        line_num = 1
        line_start = 0
        pos = 0
        code_len = len(self.code)
        while pos < code_len:
            mo = get_token(self.code, pos)
            if mo is None:
                col = pos - line_start + 1
                self.errors.append(f"Invalid token {self.code[pos]!r} at line {line_num}, column {col}")
                pos += 1
                continue
            if mo.end() == pos:
                # Defensive: avoid infinite loop if regex matches empty string
                self.errors.append(f"Lexer stuck at position {pos}, char {self.code[pos]!r}")
                pos += 1
                continue
            typ = mo.lastgroup
            val = mo.group(typ)
            if typ == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif typ == 'SKIP':
                pass
            elif typ == 'MISMATCH':
                col = mo.start() - line_start + 1
                self.errors.append(f"Invalid token {val!r} at line {line_num}, column {col}")
            else:
                col = mo.start() - line_start + 1
                self.tokens.append(Token(typ, val, line_num, col))
            pos = mo.end()
        return self.tokens

    def print_tokens(self):
        for token in self.tokens:
            print(token)
        if self.errors:
            print("\nLexical Errors:")
            for err in self.errors:
                print(err)

# For direct testing
if __name__ == "__main__":
    with open("sample_input.minipp") as f:
        code = f.read()
    lexer = Lexer(code)
    lexer.tokenize()
    lexer.print_tokens() 
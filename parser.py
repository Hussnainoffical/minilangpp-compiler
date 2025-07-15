from lexer import Lexer, Token
from minilang_ast import *
from typing import List, Optional

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, *token_types):
        token = self.current()
        if token and token.type in token_types:
            self.pos += 1
            return token
        return None

    def expect(self, *token_types):
        token = self.match(*token_types)
        if not token:
            expected = ' or '.join(token_types)
            actual = self.current().type if self.current() else 'EOF'
            self.errors.append(f"Expected {expected} but found {actual} at line {self.current().line if self.current() else '?'}")
            raise ParserError(f"Expected {expected} but found {actual}")
        return token

    def parse(self) -> Program:
        functions = []
        while self.current():
            try:
                functions.append(self.parse_function())
            except ParserError as e:
                self.synchronize()
        return Program(functions)

    def synchronize(self):
        # Skip tokens until a likely function start or EOF
        while self.current() and self.current().type not in ('INT', 'FLOAT', 'BOOL'):
            self.pos += 1

    def parse_function(self) -> FunctionDef:
        # return_type ID (params) { body }
        return_type = self.expect('INT', 'FLOAT', 'BOOL').type.lower()
        name = self.expect('ID').value
        self.expect('LPAREN')
        params = self.parse_params()
        self.expect('RPAREN')
        body = self.parse_block()
        return FunctionDef(return_type, name, params, body)

    def parse_params(self) -> List[VariableDecl]:
        params = []
        if self.current() and self.current().type in ('INT', 'FLOAT', 'BOOL'):
            while True:
                var_type = self.expect('INT', 'FLOAT', 'BOOL').type.lower()
                name = self.expect('ID').value
                params.append(VariableDecl(var_type, name))
                if not self.match('COMMA'):
                    break
        return params

    def parse_block(self) -> Block:
        self.expect('LBRACE')
        statements = []
        while self.current() and self.current().type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.expect('RBRACE')
        return Block(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        token = self.current()
        if not token:
            return None
        if token.type in ('INT', 'FLOAT', 'BOOL'):
            return self.parse_vardecl()
        elif token.type == 'ID':
            # Could be assignment or function call
            if self.lookahead(1) and self.lookahead(1).type == 'LPAREN':
                expr = self.parse_expression()
                self.expect('SEMI')
                return expr
            else:
                return self.parse_assignment()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'RETURN':
            return self.parse_return()
        elif token.type == 'LBRACE':
            return self.parse_block()
        else:
            self.errors.append(f"Unexpected token {token.type} at line {token.line}")
            self.pos += 1
            return None

    def parse_vardecl(self) -> VariableDecl:
        var_type = self.expect('INT', 'FLOAT', 'BOOL').type.lower()
        name = self.expect('ID').value
        initializer = None
        if self.match('ASSIGN'):
            initializer = self.parse_expression()
        self.expect('SEMI')
        return VariableDecl(var_type, name, initializer)

    def parse_assignment(self) -> Assignment:
        target = Identifier(self.expect('ID').value)
        self.expect('ASSIGN')
        value = self.parse_expression()
        self.expect('SEMI')
        return Assignment(target, value)

    def parse_if(self) -> If:
        self.expect('IF')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.match('ELSE'):
            else_block = self.parse_block()
        return If(cond, then_block, else_block)

    def parse_while(self) -> While:
        self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return While(cond, body)

    def parse_return(self) -> Return:
        self.expect('RETURN')
        if self.current() and self.current().type != 'SEMI':
            value = self.parse_expression()
        else:
            value = None
        self.expect('SEMI')
        return Return(value)

    def parse_expression(self) -> Expression:
        return self.parse_logical_or()

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.match('OR'):
            right = self.parse_logical_and()
            node = BinaryOp('||', node, right)
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.match('AND'):
            right = self.parse_equality()
            node = BinaryOp('&&', node, right)
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while True:
            if self.match('EQ'):
                right = self.parse_relational()
                node = BinaryOp('==', node, right)
            elif self.match('NEQ'):
                right = self.parse_relational()
                node = BinaryOp('!=', node, right)
            else:
                break
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while True:
            if self.match('LT'):
                right = self.parse_additive()
                node = BinaryOp('<', node, right)
            elif self.match('LE'):
                right = self.parse_additive()
                node = BinaryOp('<=', node, right)
            elif self.match('GT'):
                right = self.parse_additive()
                node = BinaryOp('>', node, right)
            elif self.match('GE'):
                right = self.parse_additive()
                node = BinaryOp('>=', node, right)
            else:
                break
        return node

    def parse_additive(self):
        node = self.parse_term()
        while True:
            if self.match('PLUS'):
                right = self.parse_term()
                node = BinaryOp('+', node, right)
            elif self.match('MINUS'):
                right = self.parse_term()
                node = BinaryOp('-', node, right)
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            if self.match('MUL'):
                right = self.parse_factor()
                node = BinaryOp('*', node, right)
            elif self.match('DIV'):
                right = self.parse_factor()
                node = BinaryOp('/', node, right)
            else:
                break
        return node

    def parse_factor(self):
        token = self.current()
        if token is None:
            raise ParserError("Unexpected EOF in expression")
        if token.type == 'LPAREN':
            self.match('LPAREN')
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        elif token.type == 'MINUS':
            self.match('MINUS')
            operand = self.parse_factor()
            return UnaryOp('-', operand)
        elif token.type == 'NOT':
            self.match('NOT')
            operand = self.parse_factor()
            return UnaryOp('!', operand)
        elif token.type == 'ID':
            if self.lookahead(1) and self.lookahead(1).type == 'LPAREN':
                return self.parse_function_call()
            else:
                return Identifier(self.match('ID').value)
        elif token.type in ('INT_LIT', 'FLOAT_LIT', 'TRUE', 'FALSE'):
            return self.parse_literal()
        else:
            raise ParserError(f"Unexpected token {token.type} in expression at line {token.line}")

    def parse_function_call(self) -> FunctionCall:
        name = self.expect('ID').value
        self.expect('LPAREN')
        args = []
        if self.current() and self.current().type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if not self.match('COMMA'):
                    break
        self.expect('RPAREN')
        return FunctionCall(name, args)

    def parse_literal(self) -> Literal:
        token = self.current()
        if token.type == 'INT_LIT':
            self.match('INT_LIT')
            return Literal(int(token.value), 'int')
        elif token.type == 'FLOAT_LIT':
            self.match('FLOAT_LIT')
            return Literal(float(token.value), 'float')
        elif token.type == 'TRUE':
            self.match('TRUE')
            return Literal(True, 'bool')
        elif token.type == 'FALSE':
            self.match('FALSE')
            return Literal(False, 'bool')
        else:
            raise ParserError(f"Invalid literal {token.value} at line {token.line}")

    def lookahead(self, n):
        if self.pos + n < len(self.tokens):
            return self.tokens[self.pos + n]
        return None

if __name__ == "__main__":
    with open("sample_input.minipp") as f:
        code = f.read()
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAbstract Syntax Tree:")
    ast.pretty_print()
    if parser.errors:
        print("\nSyntax Errors:")
        for err in parser.errors:
            print(err) 
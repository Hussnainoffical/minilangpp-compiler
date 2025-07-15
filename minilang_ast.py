from typing import List, Optional, Any

class ASTNode:
    """Base class for all AST nodes."""
    def pretty_print(self, indent=0):
        print(' ' * indent + self.__class__.__name__)

class Program(ASTNode):
    def __init__(self, functions: List['FunctionDef']):
        self.functions = functions
    def pretty_print(self, indent=0):
        print(' ' * indent + 'Program')
        for func in self.functions:
            func.pretty_print(indent + 2)

class FunctionDef(ASTNode):
    def __init__(self, return_type: str, name: str, params: List['VariableDecl'], body: 'Block'):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
    def pretty_print(self, indent=0):
        print(' ' * indent + f'FunctionDef {self.return_type} {self.name}')
        print(' ' * (indent + 2) + 'Params:')
        for param in self.params:
            param.pretty_print(indent + 4)
        self.body.pretty_print(indent + 2)

class VariableDecl(ASTNode):
    def __init__(self, var_type: str, name: str, initializer: Optional['Expression'] = None):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer
    def pretty_print(self, indent=0):
        print(' ' * indent + f'VariableDecl {self.var_type} {self.name}')
        if self.initializer:
            print(' ' * (indent + 2) + 'Initializer:')
            self.initializer.pretty_print(indent + 4)

class Block(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
    def pretty_print(self, indent=0):
        print(' ' * indent + 'Block')
        for stmt in self.statements:
            stmt.pretty_print(indent + 2)

class If(ASTNode):
    def __init__(self, condition: 'Expression', then_block: Block, else_block: Optional[Block] = None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    def pretty_print(self, indent=0):
        print(' ' * indent + 'If')
        print(' ' * (indent + 2) + 'Condition:')
        self.condition.pretty_print(indent + 4)
        print(' ' * (indent + 2) + 'Then:')
        self.then_block.pretty_print(indent + 4)
        if self.else_block:
            print(' ' * (indent + 2) + 'Else:')
            self.else_block.pretty_print(indent + 4)

class While(ASTNode):
    def __init__(self, condition: 'Expression', body: Block):
        self.condition = condition
        self.body = body
    def pretty_print(self, indent=0):
        print(' ' * indent + 'While')
        print(' ' * (indent + 2) + 'Condition:')
        self.condition.pretty_print(indent + 4)
        print(' ' * (indent + 2) + 'Body:')
        self.body.pretty_print(indent + 4)

class Return(ASTNode):
    def __init__(self, value: Optional['Expression'] = None):
        self.value = value
    def pretty_print(self, indent=0):
        print(' ' * indent + 'Return')
        if self.value:
            self.value.pretty_print(indent + 2)

class Assignment(ASTNode):
    def __init__(self, target: 'Identifier', value: 'Expression'):
        self.target = target
        self.value = value
    def pretty_print(self, indent=0):
        print(' ' * indent + 'Assignment')
        print(' ' * (indent + 2) + 'Target:')
        self.target.pretty_print(indent + 4)
        print(' ' * (indent + 2) + 'Value:')
        self.value.pretty_print(indent + 4)

class Expression(ASTNode):
    pass

class BinaryOp(Expression):
    def __init__(self, op: str, left: Expression, right: Expression):
        self.op = op
        self.left = left
        self.right = right
    def pretty_print(self, indent=0):
        print(' ' * indent + f'BinaryOp {self.op}')
        self.left.pretty_print(indent + 2)
        self.right.pretty_print(indent + 2)

class UnaryOp(Expression):
    def __init__(self, op: str, operand: Expression):
        self.op = op
        self.operand = operand
    def pretty_print(self, indent=0):
        print(' ' * indent + f'UnaryOp {self.op}')
        self.operand.pretty_print(indent + 2)

class Literal(Expression):
    def __init__(self, value: Any, typ: str):
        self.value = value
        self.typ = typ
    def pretty_print(self, indent=0):
        print(' ' * indent + f'Literal {self.value} ({self.typ})')

class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name
    def pretty_print(self, indent=0):
        print(' ' * indent + f'Identifier {self.name}')

class FunctionCall(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    def pretty_print(self, indent=0):
        print(' ' * indent + f'FunctionCall {self.name}')
        for arg in self.args:
            arg.pretty_print(indent + 2) 
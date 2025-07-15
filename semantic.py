from minilang_ast import *
from symbol_table import Symbol, SymbolTable, SymbolTableStack
from typing import List, Optional

class SemanticAnalyzer:
    def __init__(self):
        self.errors: List[str] = []
        self.symbol_stack = SymbolTableStack()

    def analyze(self, program: Program):
        # Global scope
        global_table = SymbolTable('global')
        self.symbol_stack.push(global_table)
        # Register all function signatures first
        for func in program.functions:
            if global_table.lookup(func.name):
                self.errors.append(f"Function redeclaration: {func.name}")
            else:
                param_types = [(p.var_type, p.name) for p in func.params]
                global_table.add(Symbol(func.name, func.return_type, 'function', param_types))
        # Analyze each function body
        for func in program.functions:
            self.analyze_function(func)
        self.symbol_stack.pop()

    def analyze_function(self, func: FunctionDef):
        func_table = SymbolTable(f'function {func.name}', self.symbol_stack.top())
        self.symbol_stack.push(func_table)
        # Add parameters
        for param in func.params:
            try:
                func_table.add(Symbol(param.name, param.var_type, 'parameter'))
            except Exception as e:
                self.errors.append(str(e))
        # Analyze body
        self.current_function_return_type = func.return_type
        self.analyze_block(func.body)
        self.symbol_stack.pop()

    def analyze_block(self, block: Block):
        block_table = SymbolTable('block', self.symbol_stack.top())
        self.symbol_stack.push(block_table)
        for stmt in block.statements:
            self.analyze_stmt(stmt)
        self.symbol_stack.pop()

    def analyze_stmt(self, stmt: ASTNode):
        if isinstance(stmt, VariableDecl):
            self.analyze_vardecl(stmt)
        elif isinstance(stmt, Assignment):
            self.analyze_assignment(stmt)
        elif isinstance(stmt, If):
            self.analyze_if(stmt)
        elif isinstance(stmt, While):
            self.analyze_while(stmt)
        elif isinstance(stmt, Return):
            self.analyze_return(stmt)
        elif isinstance(stmt, Block):
            self.analyze_block(stmt)
        elif isinstance(stmt, FunctionCall):
            self.analyze_funccall(stmt)
        else:
            self.errors.append(f"Unknown statement type: {type(stmt)}")

    def analyze_vardecl(self, decl: VariableDecl):
        table = self.symbol_stack.top()
        try:
            table.add(Symbol(decl.name, decl.var_type, 'variable'))
        except Exception as e:
            self.errors.append(str(e))
        if decl.initializer:
            init_type = self.analyze_expr(decl.initializer)
            if init_type and init_type != decl.var_type:
                self.errors.append(f"Type mismatch in initialization of {decl.name}: {decl.var_type} = {init_type}")

    def analyze_assignment(self, assign: Assignment):
        sym = self.symbol_stack.lookup(assign.target.name)
        if not sym:
            self.errors.append(f"Undeclared variable: {assign.target.name}")
            return
        value_type = self.analyze_expr(assign.value)
        if value_type and value_type != sym.type:
            self.errors.append(f"Type mismatch in assignment to {assign.target.name}: {sym.type} = {value_type}")

    def analyze_if(self, ifstmt: If):
        cond_type = self.analyze_expr(ifstmt.condition)
        if cond_type and cond_type != 'bool':
            self.errors.append(f"Condition in if must be bool, got {cond_type}")
        self.analyze_block(ifstmt.then_block)
        if ifstmt.else_block:
            self.analyze_block(ifstmt.else_block)

    def analyze_while(self, whilestmt: While):
        cond_type = self.analyze_expr(whilestmt.condition)
        if cond_type and cond_type != 'bool':
            self.errors.append(f"Condition in while must be bool, got {cond_type}")
        self.analyze_block(whilestmt.body)

    def analyze_return(self, ret: Return):
        if ret.value:
            value_type = self.analyze_expr(ret.value)
            if value_type and value_type != self.current_function_return_type:
                self.errors.append(f"Return type mismatch: expected {self.current_function_return_type}, got {value_type}")
        else:
            if self.current_function_return_type != 'void':
                self.errors.append(f"Return statement missing value for function returning {self.current_function_return_type}")

    def analyze_funccall(self, call: FunctionCall) -> Optional[str]:
        sym = self.symbol_stack.lookup(call.name)
        if not sym or sym.kind != 'function':
            self.errors.append(f"Undeclared function: {call.name}")
            return None
        param_types = sym.info
        if len(param_types) != len(call.args):
            self.errors.append(f"Function {call.name} expects {len(param_types)} args, got {len(call.args)}")
        for ((expected_type, _), arg) in zip(param_types, call.args):
            arg_type = self.analyze_expr(arg)
            if arg_type and arg_type != expected_type:
                self.errors.append(f"Function {call.name} argument type mismatch: expected {expected_type}, got {arg_type}")
        return sym.type

    def analyze_expr(self, expr: Expression) -> Optional[str]:
        if isinstance(expr, Literal):
            return expr.typ
        elif isinstance(expr, Identifier):
            sym = self.symbol_stack.lookup(expr.name)
            if not sym:
                self.errors.append(f"Undeclared identifier: {expr.name}")
                return None
            return sym.type
        elif isinstance(expr, BinaryOp):
            left = self.analyze_expr(expr.left)
            right = self.analyze_expr(expr.right)
            if expr.op in ('+', '-', '*', '/'):
                if left != right or left not in ('int', 'float'):
                    self.errors.append(f"Type error in binary op {expr.op}: {left} {expr.op} {right}")
                    return None
                return left
            elif expr.op in ('==', '!=', '<', '<=', '>', '>='):
                if left != right:
                    self.errors.append(f"Type error in comparison: {left} {expr.op} {right}")
                return 'bool'
            elif expr.op in ('&&', '||'):
                if left != 'bool' or right != 'bool':
                    self.errors.append(f"Logical op {expr.op} requires bool operands, got {left}, {right}")
                return 'bool'
        elif isinstance(expr, UnaryOp):
            operand = self.analyze_expr(expr.operand)
            if expr.op == '-' and operand in ('int', 'float'):
                return operand
            elif expr.op == '!' and operand == 'bool':
                return 'bool'
            else:
                self.errors.append(f"Unary op {expr.op} type error: got {operand}")
        elif isinstance(expr, FunctionCall):
            return self.analyze_funccall(expr)
        else:
            self.errors.append(f"Unknown expression type: {type(expr)}")
            return None

if __name__ == "__main__":
    from parser import Parser
    with open("sample_input.minipp") as f:
        code = f.read()
    from lexer import Lexer
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    print("\nSymbol Tables:")
    print(analyzer.symbol_stack)
    if analyzer.errors:
        print("\nSemantic Errors:")
        for err in analyzer.errors:
            print(err)
    else:
        print("\nNo semantic errors detected.") 
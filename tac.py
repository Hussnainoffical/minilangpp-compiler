from minilang_ast import *
from typing import List, Tuple, Any, Optional

class TACInstruction:
    def __init__(self, op: str, arg1: Any = None, arg2: Any = None, result: Any = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    def __str__(self):
        if self.op == 'label':
            return f"{self.result}:"
        elif self.op in ('goto', 'ifz', 'ifnz'):
            return f"{self.op} {self.arg1}"
        elif self.op == '=':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'param':
            return f"param {self.arg1}"
        elif self.op == 'return':
            if self.arg1 is not None:
                return f"return {self.arg1}"
            else:
                return "return"
        elif self.op == 'call':
            return f"{self.result} = {self.arg1} call {self.arg2}"
        elif self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.arg1 is not None:
            return f"{self.result} = {self.op} {self.arg1}"
        else:
            return f"{self.op} {self.result}"

class TACGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, program: Program) -> List[TACInstruction]:
        for func in program.functions:
            self.gen_function(func)
        return self.instructions

    def gen_function(self, func: FunctionDef):
        self.instructions.append(TACInstruction('label', result=func.name))
        self.gen_block(func.body)
        # Optionally, add function end marker

    def gen_block(self, block: Block):
        for stmt in block.statements:
            self.gen_stmt(stmt)

    def gen_stmt(self, stmt: ASTNode):
        if isinstance(stmt, VariableDecl):
            if stmt.initializer:
                temp = self.gen_expr(stmt.initializer)
                self.instructions.append(TACInstruction('=', temp, None, stmt.name))
        elif isinstance(stmt, Assignment):
            temp = self.gen_expr(stmt.value)
            self.instructions.append(TACInstruction('=', temp, None, stmt.target.name))
        elif isinstance(stmt, If):
            self.gen_if(stmt)
        elif isinstance(stmt, While):
            self.gen_while(stmt)
        elif isinstance(stmt, Return):
            if stmt.value:
                temp = self.gen_expr(stmt.value)
                self.instructions.append(TACInstruction('return', temp))
            else:
                self.instructions.append(TACInstruction('return'))
        elif isinstance(stmt, FunctionCall):
            self.gen_funccall(stmt)
        elif isinstance(stmt, Block):
            self.gen_block(stmt)

    def gen_if(self, ifstmt: If):
        cond_temp = self.gen_expr(ifstmt.condition)
        else_label = self.new_label()
        end_label = self.new_label() if ifstmt.else_block else None
        self.instructions.append(TACInstruction('ifz', cond_temp, None, else_label))
        self.gen_block(ifstmt.then_block)
        if ifstmt.else_block:
            self.instructions.append(TACInstruction('goto', end_label))
            self.instructions.append(TACInstruction('label', result=else_label))
            self.gen_block(ifstmt.else_block)
            self.instructions.append(TACInstruction('label', result=end_label))
        else:
            self.instructions.append(TACInstruction('label', result=else_label))

    def gen_while(self, whilestmt: While):
        start_label = self.new_label()
        end_label = self.new_label()
        self.instructions.append(TACInstruction('label', result=start_label))
        cond_temp = self.gen_expr(whilestmt.condition)
        self.instructions.append(TACInstruction('ifz', cond_temp, None, end_label))
        self.gen_block(whilestmt.body)
        self.instructions.append(TACInstruction('goto', start_label))
        self.instructions.append(TACInstruction('label', result=end_label))

    def gen_funccall(self, call: FunctionCall) -> Optional[str]:
        arg_temps = [self.gen_expr(arg) for arg in call.args]
        for temp in arg_temps:
            self.instructions.append(TACInstruction('param', temp))
        result_temp = self.new_temp()
        self.instructions.append(TACInstruction('call', call.name, len(arg_temps), result_temp))
        return result_temp

    def gen_expr(self, expr: Expression) -> str:
        # Constant folding for literals and simple binary ops
        if isinstance(expr, Literal):
            return str(expr.value).lower() if expr.typ == 'bool' else str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            left = self.gen_expr(expr.left)
            right = self.gen_expr(expr.right)
            # Constant folding
            if left.isdigit() and right.isdigit():
                folded = str(eval(f"{left}{expr.op}{right}"))
                return folded
            temp = self.new_temp()
            self.instructions.append(TACInstruction(expr.op, left, right, temp))
            return temp
        elif isinstance(expr, UnaryOp):
            operand = self.gen_expr(expr.operand)
            temp = self.new_temp()
            self.instructions.append(TACInstruction(expr.op, operand, None, temp))
            return temp
        elif isinstance(expr, FunctionCall):
            return self.gen_funccall(expr)
        else:
            raise Exception(f"Unknown expression type: {type(expr)}")

if __name__ == "__main__":
    from parser import Parser
    from lexer import Lexer
    with open("sample_input.minipp") as f:
        code = f.read()
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    tacgen = TACGenerator()
    tac = tacgen.generate(ast)
    print("\nThree Address Code (TAC):")
    for instr in tac:
        print(instr) 
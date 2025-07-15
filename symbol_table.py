from typing import Dict, Optional, List

class Symbol:
    def __init__(self, name: str, sym_type: str, kind: str, info=None):
        self.name = name
        self.type = sym_type  # int, float, bool, function
        self.kind = kind      # variable, function, parameter
        self.info = info      # Additional info (e.g., params for functions)
    def __str__(self):
        return f"Symbol(name={self.name}, type={self.type}, kind={self.kind}, info={self.info})"

class SymbolTable:
    def __init__(self, scope_name: str, parent: Optional['SymbolTable'] = None):
        self.scope_name = scope_name
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
    def add(self, symbol: Symbol):
        if symbol.name in self.symbols:
            raise Exception(f"Redeclaration of {symbol.name} in scope {self.scope_name}")
        self.symbols[symbol.name] = symbol
    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None
    def __str__(self):
        out = f"Scope: {self.scope_name}\n"
        for sym in self.symbols.values():
            out += f"  {sym}\n"
        return out

class SymbolTableStack:
    def __init__(self):
        self.stack: List[SymbolTable] = []
    def push(self, table: SymbolTable):
        self.stack.append(table)
    def pop(self):
        return self.stack.pop()
    def top(self) -> SymbolTable:
        return self.stack[-1]
    def lookup(self, name: str) -> Optional[Symbol]:
        for table in reversed(self.stack):
            sym = table.lookup(name)
            if sym:
                return sym
        return None
    def __str__(self):
        return '\n'.join(str(table) for table in self.stack) 
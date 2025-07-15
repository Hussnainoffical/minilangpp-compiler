# MiniLang++ Compiler Front-End
Front-end compiler for a simplified C-like language (MiniLang++) with lexer, parser, semantic analysis, and TAC generation, built in Python
This repository contains the complete front-end compiler for MiniLang++, a simplified imperative programming language. The compiler includes lexical analysis, parsing, semantic analysis, scoped symbol tables, and intermediate code generation in the form of Three Address Code (TAC).

The project was developed for the Compiler Construction (CS3045) course as a full-featured educational tool that mirrors real-world compiler architecture.

Features
Lexical Analyzer

Tokenizes keywords, identifiers, literals, operators, and delimiters

Detects and reports lexical errors with line/column context

Recursive Descent Parser

LL(1) grammar implementation

Builds an Abstract Syntax Tree (AST)

Handles syntactic error detection and recovery

Semantic Analyzer

Constructs nested, scoped symbol tables

Validates:

Type correctness

Identifier declarations

Function redefinitions

Return type consistency

Intermediate Code Generator

Outputs clean and structured Three Address Code (TAC)

Supports function calls, conditionals, temporaries

Performs basic optimizations (constant folding, dead code elimination)

Example Code (MiniLang++)
c
Copy
Edit
int max(int a, int b) {
  if (a > b) {
    return a;
  } else {
    return b;
  }
}

int main() {
  int x = 10;
  int y = 20;
  int z = max(x, y);
  return 0;
}
Example AST (Text Visualization)
sql
Copy
Edit
Program
  FunctionDef int max
    Params:
      VariableDecl int a
      VariableDecl int b
    Block
      If
        Condition:
          BinaryOp >
            Identifier a
            Identifier b
        Then:
          Block
            Return Identifier a
        Else:
          Block
            Return Identifier b
  FunctionDef int main
    Block
      VariableDecl int x = 10
      VariableDecl int y = 20
      VariableDecl int z = max(x, y)
      Return 0
Example Symbol Tables
sql
Copy
Edit
Scope: global
  max    : function, returns int, params (int a, int b)
  main   : function, returns int, params ()

Scope: max
  a      : parameter, int
  b      : parameter, int

Scope: main
  x      : variable, int
  y      : variable, int
  z      : variable, int
Sample TAC Output
vbnet
Copy
Edit
max:
t1 = a > b
ifz t1 goto L1
return a
goto L2
L1:
return b
L2:

main:
x = 10
y = 20
param x
param y
t2 = call max, 2
z = t2
return 0
Project Structure
bash
Copy
Edit
minilangpp-compiler/
├── main.py                 # Compiler orchestrator
├── lexer.py                # Regex-based lexical analyzer
├── parser.py               # Recursive descent parser
├── minilang_ast.py         # AST node definitions
├── semantic.py             # Type checking and semantic analysis
├── symbol_table.py         # Scoped symbol table manager
├── tac.py                  # Three Address Code generator
├── tests/
│   ├── valid_sample.minipp
│   └── invalid_sample.minipp

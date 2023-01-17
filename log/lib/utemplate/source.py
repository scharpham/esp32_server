# (c) 2014-2019 Paul Sokolovsky. MIT license.
from . import compiled


class Compiler:

    START_CHAR = "{"
    STMNT = "%"
    STMNT_END = "%}"
    EXPR = "{"
    EXPR_END = "}}"

    def __init__(self, file_in, file_out, indent=0, seq=0, loader=None):
        self.file_in = file_in
        self.file_out = file_out
        self.loader = loader
        self.seq = seq
        self._indent = indent
        self.stack = []
        self.in_literal = False
        self.flushed_header = False
        self.args = "*a, **d"

    def indent(self, adjust=0):
        if not self.flushed_header:
            self.flushed_header = True
            self.indent()
            self.file_out.write("def render%s(%s):\n" % (str(self.seq) if self.seq else "", self.args))
            self.stack.append("def")
        self.file_out.write("    " * (len(self.stack) + self._indent + adjust))

    def literal(self, s):
        if not s:
            return
        if not self.in_literal:
            self.indent()
            self.file_ou
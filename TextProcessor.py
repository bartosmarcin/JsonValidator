__author__ = 'marcin'
from unicodedata import category


class Processor:

    def __init__(self, file):
        self.file = file
        self.line_num = 1
        self.col_num = 0

    def get_token(self):
        c = self.file.read(1)
        self.col_num += 1

        if not c:
            return "EOF"

        if c == "\n":
            self.line_num += 1
            self.col_num = 0

        if c.isspace():
            return self.get_token()

        return c


class Validator:

    def __init__(self, file):
        self.file = file
        self.processor = Processor(file)
        self.token = self.processor.get_token()

    def next_token(self):
        self.token = self.processor.get_token()

    def append_next_token(self, n=1):
        for i in range(n):
            self.token += self.processor.get_token()


    def check_token_and_get_next(self, token):
        if not self.token == token:
            return False
        self.next_token()
        return True

    def validation_error(self, expected="", line=None, column=None):
        if line is None:
            line = self.processor.line_num
        if column is None:
            column = self.processor.col_num
        raise ValueError("Error in line " + str(line) + ", column " + str(column) +
                         ". Expected " + expected + " got " + self.token)

    def validate(self):
        self.json()
        self.eof()

    def json(self):
        if self.token == "{":
            self.obj()
        elif self.token == "[":
            self.arr()
        else:
            self.validation_error("{ or [")

    def obj(self):
        self.op_brace()
        if not self.token == "}":
            self.flds()
        self.cl_brace()

    def arr(self):
        self.op_bracket()
        if not self.token == "]":
            self.elements()
        self.cl_bracket()

    def elements(self):
        self.value()
        if self.check_token_and_get_next(","):
            return self.elements()

    def flds(self):
        self.pair()
        if self.check_token_and_get_next(","):
            self.flds()
        elif self.token == "}":
            return
        else:
            self.validation_error(", or }")

    def pair(self):
        self.string()
        self.colon()
        self.value()

    def value(self):
        if self.token == "\"":
            self.string()
        elif self.token.isdigit() or self.token == "-":
            self.figure()
        elif self.token == "{":
            self.obj()
        elif self.token == "[":
            self.arr()
        elif self.token == "t":
            self.true()
        elif self.token == "f":
            self.false()
        elif self.token == "n":
            self.null()
        else:
            self.validation_error("value(string, number, object, array, true, false or null)")

    def string(self):
        self.quot_mark()
        #TODO obsluga escapowanych str
        if not self.token == "\"":
            self.chars()
        self.quot_mark()

    def chars(self):
        self.char()
        if not self.token == "\"":
            self.chars()

    def figure(self):
        self.check_token_and_get_next("-")
        self.number()

    def number(self):
        self.digits()
        if self.token == ".":
            self.fraction()
        if self.token in {"e", "E"}:
            self.exp()

    def digits(self):
        self.digit()
        if self.token.isdigit():
            self.digits()

    def digit(self):
        if not self.token.isdigit():
            self.validation_error("digit")
        else:
            self.token = self.processor.get_token()

    def fraction(self):
        self.dot()
        self.digits()

    def exp(self):
        self.e()
        self.digits()

    def e(self):
        if not self.token in {"e", "E"}:
            self.validation_error("e")
        self.next_token()
        if self.token in {"+", "-"}:
            self.next_token()

    def dot(self):
        if not self.check_token_and_get_next("."):
            self.validation_error(".")

    def eof(self):
        if not self.check_token_and_get_next("EOF"):
            self.validation_error("end of file")

    def op_brace(self):
        if not self.check_token_and_get_next("{"):
            self.validation_error("{")

    def cl_brace(self):
        if not self.check_token_and_get_next("}"):
            self.validation_error("}")

    def op_bracket(self):
        if not self.check_token_and_get_next("["):
            self.validation_error("[")

    def cl_bracket(self):
        if not self.check_token_and_get_next("]"):
            self.validation_error("]")

    def coma(self):
        if not self.check_token_and_get_next(","):
            self.validation_error(",")

    def colon(self):
        if not self.check_token_and_get_next(":"):
            self.validation_error(":")

    def quot_mark(self):
        if not self.check_token_and_get_next("\""):
            self.validation_error("\".")

    def char(self):
        if category(self.token) == 'Cc':
            self.validation_error("character")
        if self.token == "\\":
            self.next_token()
            self.next_token()
        elif self.token == "\"":
            self.validation_error("character")
        else:
            self.next_token()

    def true(self):
        self.append_next_token(3)
        if not self.check_token_and_get_next("true"):
            self.validation_error("true")

    def false(self):
        self.append_next_token(4)
        if not self.check_token_and_get_next("false"):
            self.validation_error("false")

    def null(self):
        self.append_next_token(3)
        if not self.check_token_and_get_next("null"):
            self.validation_error("null")

with open("test") as f:
    validator = Validator(f)
    try:
        validator.validate()
        print("Valid JSON file")
    except ValueError as e:
        print(e.__str__())


from random import randint
import re
import os

skills = {
    'Initiative': 'dex',  # simplification of initiative
    'Strength': 'str',  # the base stats
    'Constitution': 'con',
    'Dexterity': 'dex',
    'Intelligence': 'int',
    'Wisdom': 'wis',
    'Charisma': 'cha',  # implement other skills
    'Athletics': 'str',
    'Acrobatics': 'dex',
    'Sleight of Hand': 'dex',
    'Stealth': 'dex',
    'Arcana': 'int',
    'History': 'int',
    'Investigation': 'int',
    'Nature': 'int',
    'Religion': 'int',
    'Animal Handling': 'wis',
    'Insight': 'wis',
    'Medicine': 'wis',
    'Perception': 'wis',
    'Survival': 'wis',
    'Deception': 'cha',
    'Intimidation': 'cha',
    'Performance': 'cha',
    'Persuasion': 'cha'
}
stats = [
    "str", "con", "dex", "int", "wis", "cha"
]
mods = {
    'strmod': 'Strength',  # the base stats
    'conmod': 'Constitution',
    'dexmod': 'Dexterity',
    'intmod': 'Intelligence',
    'wismod': 'Wisdom',
    'chamod': 'Charisma',
    'promod': 'Proficiency'
}
dice = []


def autocomplete(message, options, case_sens=False):
    """ attempt to autocomplete message amongs options """
    if not message:
        return None
    if not case_sens:
        message = message.lower()

    if not case_sens:
        found = filter(
            lambda option: option.lower().startswith(message), options)
    else:
        found = filter(lambda option: option.startswith(message), options)

    return tuple(found)


def roll_die(i): return randint(1, i)
def d20(): return roll_die(20)

#     return rolls, result


class Die:
    def __init__(self, arg):
        self.type = -1
        mult, die = arg.split("d", maxsplit=1)

        # find when the die number ends
        for c, _ in enumerate(die):
            try:
                int(die[c+1])
            except:
                break

        self.appendage = Appendage(die[c+1:])
        mult, die = int(mult), int(die[:c+1])
        self.mult = mult
        self.die = die
        self.evaulated = False
        self.tossed = []
        self.value = 0
        self.average = Value(mult * (die/2 + 0.5))

    def __repr__(self):
        return f"Die<{self.mult}d{self.die}{self.appendage}>"

    @staticmethod
    def valid(arg):
        die_regex = r"^[\d]+d[\d]+([kd][hl][1-9]+)?$"
        if re.search(die_regex, str(arg)):
            return True
        return False

    def evaluate(self):
        if self.evaulated:
            self.value

        self.tossed = tuple(roll_die(self.die) for i in range(self.mult))
        print(f"Evaluating die {self}: {self.tossed}")
        if not self.appendage.empty:
            self.value = self.appendage.evaluate(self)
        else:
            self.value = Value(sum(self.tossed))

        dice.append(list(self.tossed))

        return self.value

    def copy(self):
        return Die(f"{self.mult}d{self.die}")


class Appendage:
    def __init__(self, arg):
        self.str = arg
        self.empty = False
        if len(arg) == 0:
            self.empty = True
            return
        # take an arg similar to "kh2"
        self.keep = 1 if arg[0] == 'k' else -1
        self.highest = 1 if arg[1] == 'h' else -1
        self.amount = int(arg[2:])

    def evaluate(self, die: Die):

        # [1, 3, 4, 6] dh1 -> [1, 3, 4] = 8
        # [1, 3, 4, 6] kh1 -> [6]       = 6
        # [1, 3, 4, 6] kl2 -> [1, 3]    = 4
        # [1, 3, 4, 6] dl2 -> [4, 6]    = 10
        # [1, 3, 4, 6] dh2 -> [1, 3]    = 4

        die_len = len(die.tossed)

        toss = list(die.tossed)

        # how many die do we end up with?
        if self.keep > 0:
            end_die_len = self.amount
        else:
            end_die_len = die_len - self.amount

        # do we take the highest or lowest?
        toss.sort(reverse=self.highest * self.keep > 0)
        # print(toss, toss[:end_die_len], sum(toss[:end_die_len]))

        # take that many die
        return Value(sum(toss[:end_die_len]))

    def __repr__(self):
        return f"{self.str}"


class Value:
    def __init__(self, val):
        self.val = float(val)
        self.type = -1

    def __add__(self, other):
        if type(other) == Value:
            return Value(self.val + other.val)
        else:
            return Value(self.val + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return Value(self.val - other.val)

    def __mul__(self, other):
        if type(other) == Value:
            return Value(self.val * other.val)
        else:
            return Value(self.val * other)

    def __pow__(self, other):
        if type(other) == Value:
            return self.val ** other.val
        else:
            return Value(self.val ** other)

    def __repr__(self):
        return f"Val<{self.val}>"

    def __int__(self):
        return int(self.val)

    def __float__(self):
        return float(self.val)

    @staticmethod
    def valid(val):
        try:
            float(val)
        except:
            return False
        return True

    def evaluate(self):
        return self


class Operation:

    Operators = "+-*^"

    def __init__(self, op):
        self.op = op
        self.type = {
            "+": 0,
            "-": 1,
            "*": 2,
            "^": 3
        }[op]

    def __repr__(self):
        return f"Opr<{self.op}>"

    def operate(self, left: Value, right: Value) -> Value:
        if self.op == '+':
            return Value(left.evaluate() + right.evaluate())
        if self.op == '-':
            return Value(left.evaluate() - right.evaluate())
        if self.op == '*':
            return Value(left.evaluate() * right.evaluate())
        if self.op == '^':
            if type(left) == Die and type(right):
                return Value(sum(left.copy().evaluate() for i in range(int(right))))
            return Value(left.evaluate() ** right.evaluate())


def preprocess(arg, char):
    """
    do the preprocessing for a DnD roll
    converts skill checks to their respective die
    """

    string = "".join(arg).replace(" ", "")
    stringcpy = string

    # pre process modifiers
    for mod in mods:
        if not mod in stringcpy:
            continue

        roll_type = mods[mod]

        if roll_type == 'Proficiency':
            stringcpy = stringcpy.replace(mod, str(char.get_proficiency()))
        else:
            stringcpy = stringcpy.replace(
                mod, str(char.get_modifier(roll_type)))

    c = 0
    # pre process all skill checks and advantage
    while c < len(string):
        _c = 1
        substring = string[c:c+_c]

        # if current substring is a skill
        if autocomplete(substring, skills):

            while autocomplete(substring, skills) and c+_c <= len(string):

                _c += 1
                substring = string[c:c+_c]

            _c -= 1
            substring = string[c:c+_c]

            into = autocomplete(substring, skills)
            roll_type = into[0]

            if len(into) > 1 or len(substring) < 2:
                c += 1
                continue

            # test if the following argument autocompletes into
            # advantage or disadvantage

            _d = 1
            subpend = string[c+_c: c+_c+_d]
            append = ""
            if autocomplete(subpend, ["Advantage", "Disadvantage"]):
                while autocomplete(subpend, ["Advantage", "Disadvantage"]) and c+_c+_d <= len(string):

                    _d += 1
                    subpend = string[c+_c: c+_c+_d]

                _d -= 1
                subpend = string[c+_c: c+_c+_d]
                into = autocomplete(subpend, ["Advantage", "Disadvantage"])

                if not into or len(into) > 1 or len(substring) < 2:
                    _d += 1
                    continue

                append = into[0]

            if append in ["Advantage", "Disadvantage"]:
                if append == "Advantage":
                    replacement = f"2d20kh1+{char.get_modifier(roll_type)}"
                else:
                    replacement = f"2d20kl1+{char.get_modifier(roll_type)}"
            else:
                replacement = f"1d20+{char.get_modifier(roll_type)}"

            if append in ["Advantage", "Disadvantage"]:
                stringcpy = stringcpy.replace(subpend, "", 1)
                c += len(subpend)
            stringcpy = stringcpy.replace(substring, replacement, 1)
            c += len(substring) - 1

        c += 1

    return stringcpy


def tokenize(string):
    """parse a list of 
    """

    # construct the unparsed tokens

    blocks = []
    i = 0

    # add all operators to the list
    while i < len(string):
        if string[i] in Operation.Operators:
            blocks.append(string[0:i])
            blocks.append(Operation(string[i]))
            string = string[i+1:]
            i = 0

        i += 1
    blocks.append(string)

    # convert non operators to their class
    for c, block in enumerate(blocks):

        if Value.valid(block):
            blocks[c] = Value(block)
        elif Die.valid(block):
            blocks[c] = Die(block)

    # replace empty values with 0
    final_blocks = [x if (x != '') else Value(0) for x in blocks]
    return final_blocks


def parse_exponent(tokens):
    # parse a list of tokens for exponents and return the result

    after_exponent = []
    skip_next = False
    # evaluate exponents first
    for c, _ in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        if tokens[c].type != Operation('^').type:
            after_exponent.append(tokens[c])
            continue
        after_exponent.pop(-1)
        after_exponent.append(tokens[c].operate(tokens[c-1], tokens[c+1]))
        skip_next = True

    return after_exponent


def parse_multiplication(tokens):
    # parse a list of tokens for multiplication and return the result
    after_multi = []
    skip_next = False
    # evaluate multiplication
    for c, _ in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        if tokens[c].type != Operation('*').type:
            after_multi.append(tokens[c])
            continue
        after_multi.pop(-1)
        after_multi.append(tokens[c].operate(tokens[c-1], tokens[c+1]))
        skip_next = True

    return after_multi


def parse_remainder(tokens, average):
    # parse a list of tokens for addition and subtraction and return the result
    result = Value(0)

    # evaluate all die in the tokens
    for c, _ in enumerate(tokens):
        if type(tokens[c]) != Die:
            continue

        if type(tokens[c]) == Die and average:
            tokens[c] = tokens[c].average
        else:

            tokens[c] = tokens[c].evaluate()

    result = tokens[0]

    # evaluate multiplication
    for c, _ in enumerate(tokens):
        if type(tokens[c]) != Operation:
            continue
        result = (tokens[c].operate(result, tokens[c+1]))

    return result


def parse_no_pre(arg):
    global dice
    dice = []
    _tokens = tokenize(arg)
    _parse_exponent = parse_exponent(_tokens)
    _parse_multiplication = parse_multiplication(_parse_exponent)
    _parse_remainder = parse_remainder(_parse_multiplication, False)

    formatted_dice = ", ".join((str(d) for d in dice))

    return arg, formatted_dice, _parse_remainder


def parse(arg, char, average=False):
    global dice
    dice = []
    _preprocess = preprocess(arg, char)
    _tokens = tokenize(_preprocess)
    _parse_exponent = parse_exponent(_tokens)
    _parse_multiplication = parse_multiplication(_parse_exponent)
    _parse_remainder = parse_remainder(_parse_multiplication, average)

    formatted_dice = ", ".join((str(d) for d in dice))

    return _preprocess, formatted_dice, _parse_remainder

from random import randint
import player

skills = {
    'Initiative' : 'dex', # simplification of initiative
    'Strength' : 'str', # the base stats
    'Constitution' : 'con',
    'Dexterity' : 'dex',
    'Intelligence' : 'int',
    'Wisdom' : 'wis',
    'Charisma' : 'cha', # implement other skills
    'Athletics' : 'str',
    'Acrobatics': 'dex',
    'Sleight of Hand': 'dex',
    'Stealth' : 'dex',
    'Arcana' : 'int',
    'History' : 'int',
    'Investigation': 'int',
    'Nature' : 'int',
    'Religion' : 'int',
    'Animal Handling' : 'wis',
    'Insight' : 'wis',
    'Medicine' : 'wis',
    'Perception' : 'wis',
    'Survival' : 'wis',
    'Deception' : 'cha',
    'Intimidation' : 'cha',
    'Performance' : 'cha',
    'Persuasion' : 'cha'
    }
stats = [
    "str", "con", "dex", "int", "wis", "cha"
    ]

def autocomplete(message, options, case_sens = False):
    """ attempt to autocomplete message amongs options """
    if not message:
        return None
    if not case_sens:
        message = message.lower()
    for option in options:
        if not case_sens:
            if option.lower().startswith(message):
                return option
        else:
            if option.startswith(message):
                return option
    return None


def roll_die(i): return randint(1,i)
def d20(): return roll_die(20)


def roll_skill(char : player.Character, skill:str, prof=0, adv=0):
    rolls = [d20() for i in range(1 + abs(adv))]
    mod = char.get_modifier(skill)

    if adv >= 0:
        result = max(rolls) + mod + int((prof * char.get_proficiency()))
    else:
        result = min(rolls) + mod + int((prof * char.get_proficiency()))

    return rolls, int(result)

def roll_initiative(char : player.Character, adv = False):
    rolls = [d20() for i in range(1 + adv)]
    result = max(rolls) + char.get_initiative()

    return rolls, result

    
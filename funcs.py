from re import search

def autocomplete(message, options, case_sens = False):
    """ attempt to autocomplete message amongs options 
    
    return None if none was found
    """
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

def split(string:str, match: str, re:bool=False) -> tuple:
    # split some str s up into a tuple, whenever it encounters
    # character in ch
    # optionally, use a regex search to match
    splitted = []
    split_dexes = []

    for c, ch in enumerate(string[::-1]):
        if ch in match:
            split_dexes.append(len(string) - c)

    print(split_dexes)

    for c in range(len(split_dexes) + 1):
        if c == 0:
            splitted.append(string[split_dexes[c]:])
        elif c < len(split_dexes):
            splitted.append(string[split_dexes[c]:split_dexes[c-1]-1])
        else:
            splitted.append(string[:split_dexes[c-1]])

    return splitted[::-1]





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

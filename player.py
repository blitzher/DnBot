from roll_module import skills, autocomplete

class Character:
    def __init__(self, name="None", level=0, _str=0, dex=0, con=0, _int=0, wis=0, cha=0):
        self.name = name
        self.level = level
        self.stats = {
            'str':int(_str),
            'dex':int( dex),
            'con':int( con),
            'int':int(_int),
            'wis':int( wis),
            'cha':int( cha)
        }
        self.proficiencies = {}
        self.owner = 0


    def __str__(self):
        return f"<Character Object at lvl {self.level}>"

    # instantiate a new character object from a json object
    @staticmethod
    def from_json(obj):
        char = Character(
            obj['name'],
            obj['level'],
            _str=obj['stats']['str'],
            dex =obj['stats']['dex'],
            con =obj['stats']['con'],
            _int=obj['stats']['int'],
            wis =obj['stats']['wis'],
            cha =obj['stats']['cha']
            )
        char.set_owner(obj['owner'])
        for skill, value in obj['proficiencies'].items():
            char.set_proficiency(skill, value)
        return char

    # convert a character object to a json object
    def to_json(self):
        return {
            'name' :str(self.name),
            'level':int(self.level),
            'stats':self.stats,
            'proficiencies':self.proficiencies,
            'owner':self.owner
            }

    def set_owner(self, user):
        if type(user) != str:
            user = str(user)
        if user == "0":
            user = 0
        self.owner = user

    def set_proficiency(self, skill, value):
        if autocomplete(skill, skills):
            self.proficiencies[skill] = value
            return True
        else:
            return False
    
            

    def set_level(self, value):
        self.level = value

    def set_stat(self, stat, value):
        self.stats[stat] = value

    def get_modifier(self, stat):
        if stat in self.proficiencies:
            proficiency_modifier = self.proficiencies[stat] * self.get_proficiency()
        else:
            proficiency_modifier = 0
        stat_type = skills[stat]
        return proficiency_modifier + (self.stats[stat_type]-10) // 2

    def get_initiative(self):
        return self.get_modifier('dex')

    def get_proficiency(self):
        return 2 + ((int(self.level-1)) // 4)

class Roll:
    def __init__(self, name="None", roll="0", owner=0):
        self.name = name
        self.roll = roll
        self.owner = owner

    @staticmethod
    def from_json(d):
        return Roll(name=d['name'], roll=d['roll'], owner=d['owner'])

    def to_json(self):
        d = {
            'name' : str(self.name),
            'roll' : self.roll,
            'owner': str(self.owner)
        }
        return d

    def get_roll(self):
        return self.roll

    def set_owner(self, user):
        self.owner = user


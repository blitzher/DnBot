
class Character:
    def __init__(self, name, level, _str=0, dex=0, con=0, _int=0, wis=0, cha=0):
        self.name = name
        self.level = level
        self.stats = {
            'str':_str,
            'dex': dex,
            'con': con,
            'int':_int,
            'wis': wis,
            'cha': cha
        }
        self.owner = None

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
        return char

    # convert a character object to a json object
    def to_json(self):
        return {
            'name' :self.name,
            'level':self.level,
            'stats':self.stats,
            'owner':self.owner
            }

    def set_owner(self, user):
        self.owner = user

    def set_level(self, value):
        self.level = value

    def set_stat(self, stat, value):
        self.stats[stat] = value

    def get_modifier(self, stat):
        return (self.stats[stat]-10) // 2

    def get_initiative(self):
        return self.get_modifier('dex')

    def get_proficiency(self):
        return 2 + (self.level-1) // 4

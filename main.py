"""
discord bot to handle rerolls for characters in DnD
"""
import discord, os, json, re
import argparser, player
import roll_module
from textwrap import dedent

token = os.getenv('DISCORD')

if not token:
    try:
        with open("token.json", "r") as f:
            token = json.load(f)['token']
    except:
        raise AttributeError("Couldn't locate token in environment variables or token file")
prefix = "."
with open('characters.json', 'r') as f:
    jfile = json.load(f)
    all_characters = jfile['characters']
    all_rolls = jfile['rolls']

class BotClient(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.active_characters = [player.Character.from_json(char) 
                                  for char in all_characters]
        self.active_rolls = [player.Roll.from_json(roll)
                                for roll in all_rolls]
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord')

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return # Don't respond to own messages
        
        if message.content.startswith('.'):
            command = message.content[1:]
            command = command.split(" ")
            arg = command[1:]
            command = command[0]
            await self.handle_commands(command, arg, message)

    async def handle_commands(self, command, arg:list, message:discord.Message):

        if command == 'help':
            action_display = f"""
                ```
                Usable commands:
                - {prefix}add <name> <lvl> str:<i> con:<i> dex:<i> int:<i> wis:<i> cha:<i>
                    
                - {prefix}roll <skill>
                - {prefix}roll <dnd-dice>
                - {prefix}roll <saved-roll>

                - {prefix}me

                - {prefix}set <stat> <value>

                - {prefix}save <name> <dnd-dice>

                - {prefix}claim <name>

                - {prefix}help <command>
                ```
            """

            if len(arg) > 0:

                add_message = f"""
                    ```
                    - {prefix}add <name> <lvl> str:<i> con:<i> dex:<i> int:<i> wis:<i> cha:<i>
                        Add a character to the database, and automatically claim them as your own

                        Example usage:
                        {prefix}add Manly_Man 17 str:20 dex:14 con:12 int:4 wis:5 cha:3
                    ```"""
                roll_message = f"""
                    ```
                    - {prefix}roll <skill>
                    - {prefix}roll <dnd-dice>
                    - {prefix}roll <saved-roll>

                        Roll some dice. Use {prefix}roll <skill> <appendage> to add different kinds of rolls
                        These can be;
                        +:  proficiency
                        ++: expertice
                        /:  bardic proficiency
                        x:  advantage
                        d:  disadvantage

                        Example usage:
                        {prefix}roll acro +x        <:> Rolls Acrobatics with proficiency and advantage
                        {prefix}roll 3d8 + 3 * 2    <:> Rolls 3d8, and adds 6, and sums them up
                        {prefix}roll shortsword_hit <:> Rolls a saved roll, in this case, shortsword
                        ```"""
                me_message = f"""
                    ```
                    - {prefix}me
                        Display your currently claimed character
                        ```"""
                set_message = f"""
                    ```
                    - {prefix}set <stat> <value>
                        Set the stat, str, int or another, to some new value

                        Example usage:
                        {prefix}set strength 20
                        ```"""
                save_message = f"""
                    ```
                    - {prefix}save <name> <dnd-dice>
                        Save some type of roll into the database. Can be used for weapons, spells
                        or whatever you wish.

                        Example usage:
                        {prefix}save shortsword-hit 1d20+2
                        {prefix}save shortsword-atk 1d6+1
                        ```"""
                claim_message = f"""
                    ```
                    - {prefix}claim <name>
                        Claim some character as your own. Character must be unowned, and your
                        current character will be left unowned.

                        Example usage:
                        {prefix}claim Manly_Man
                        ```"""

                switcher = {
                    'add':add_message,
                    'roll':roll_message,
                    'me':me_message,
                    'set':set_message,
                    'save':save_message,
                    'claim':claim_message
                }

                action_display = switcher[arg[0]]


            await message.channel.send(dedent(action_display))

        if command == 'add':
            char = self.parse_player(message)
            
            if char:
                char.set_owner(message.author)
                self.active_characters.append(char)
                self.save_json()
                action_display = f"Succesfully added {char.name} to database, claimed by {message.author.mention}!"
            else:
                action_display = f"Could not interpret {message.content} as a valid character!"
            await message.channel.send(action_display)

        if command == 'roll':
            char, _ = self.get_character(message.author)
            
            saved_roll = self.get_saved_roll(arg[0], message.author)
            if saved_roll:
                die, tossed, result = roll_module.parse(saved_roll, char)
            else:
                die, tossed, result = roll_module.parse(arg, char)

            action_display = f'Rolled `{die}` for {message.author.mention} : `{tossed}` with result **{int(result)}**'
            await message.channel.send(action_display)

        if command == 'me':
            char, _ = self.get_character(message.author)
            if not char:
                action_display = "Could not find character belonging to you!"
                await message.channel.send(action_display)
                return
            else:
                action_display = self.format_character(char.to_json())
                await message.channel.send(embed=action_display)

        if command == 'set':
            # set a skill for your owned character
            _, index = self.get_character(message.author)
            skill = roll_module.skills[roll_module.autocomplete(arg[0], roll_module.skills)]

            # make sure a regular stat was entered
            if skill not in roll_module.stats:
                action_display = f"Cannot set {arg[0]} on character!"
                await message.channel.send(action_display)
                return False

            # make sure the following argument is an int
            try:
                setto = int(arg[1])
            except Exception as _:
                action_display = f"Cannot set {skill} to {arg[1]}!"
                await message.channel.send(action_display)
                return False

            self.active_characters[index].stats[skill] = setto

            action_display = f"Succesfully updated `{skill}` for `{char.name}` to `{setto}`"
            await message.channel.send(action_display)

        if command == 'save':
            # save a type of roll, typically a weapon or spell
            char, _ = self.get_character(message.author)
            name = arg[0]
            roll = roll_module.parse(arg[1:], char)
            if roll:
                roll = player.Roll(name=name, roll=arg[1:], owner=str(message.author))
                self.active_rolls.append(roll)
                self.save_json()
                action_display = f"Succesfully saved `{name}` to database, claimed by {message.author.mention}!"
            else:
                action_display = f"Could not interpret {str(arg[1:])} as a valid roll!"
            await message.channel.send(action_display)

        if command == 'claim':          

            action_display = False
            for _, ch in enumerate(self.active_characters):
                if ch.name == arg[0] and ch.owner:
                    action_display = f"Character `{ch.name}` is already claimed!"
                elif ch.name == arg[0] and not ch.owner:

                    
                    # if you already own a character, remove you as owner
                    self.disown_character(message.author)
                    # set message author to owner
                    ch.set_owner(str(message.author))
                    self.save_json()
                    action_display = f"Succesfully claimed `{ch.name}`!"
                    break
            if not action_display:
                action_display = f"Character `{arg[0]}` could not be found. Add them using {prefix}add!"

            await message.channel.send(action_display)
                

    def format_character(self, char:dict) -> discord.Embed:

        def get(s):
            return "{:3}".format(char['stats'][s])

        embed = discord.Embed(title=char['name'])

        embed.description = f"""
        **D&D Character**
        Owner: `{char['owner']}` at level `{char['level']}`

        **Stats**
        `STR:{get('str')} - CON:{get('con')} - DEX:{get('dex')}`
        `INT:{get('int')} - WIS:{get('wis')} - CHA:{get('cha')}`
        """.strip()

        #embed.add_field()
        return embed

    def get_character(self, owner : str) -> (player.Character, int):
        for c, char in enumerate(self.active_characters):
            if char.owner == str(owner):
                return char, c
        return None

    def get_saved_roll(self, roll_name:str, owner : discord.Member) -> player.Roll:
        for roll in self.active_rolls:
            if roll.owner == str(owner) and roll.name == roll_name:
                return roll.get_roll()
        return 

    def disown_character(self, owner : str) -> bool:
        char = self.get_character(owner)
        if char:
            _, index = char
            self.active_characters[index].set_owner(0)
            return True
        return False

    def save_json(self):
        d = {}
        d['characters'] = [char.to_json() for char in self.active_characters]
        d['rolls'] = [roll.to_json() for roll in self.active_rolls]
        with open("characters.json", 'w') as f:
            json.dump(d, f, indent=2)

    def parse_player(self, message : discord.Message):
        args = ('name','level')
        kwargs = {
            "str":0,
            "dex":0,
            "con":0,
            "int":0,
            "wis":0,
            "cha":0
        }
        
        try:
            parsed = argparser.parse(message, args, kwargs) 
            # sort out namespace error, with str and int
            parsed['_str'] = parsed.pop('str')
            parsed['_int'] = parsed.pop('int')
            
            # pylint: disable=unexpected-keyword-arg
            char = player.Character(**parsed)
            return char
        except Exception as e: # if encountering an error parsing arg as a player, return false
            print(e)
            return False  


def main():
    client = BotClient()
    try:
        client.run(token)
    finally:
        client.save_json()

if __name__ == '__main__':
    main()
"""
discord bot to handle rerolls for characters in DnD
"""
import discord, os, json, re
import argparser, player
import roll_module

token = os.getenv('DISCORD')

if not token:
    try:
        with open("token.json", "r") as f:
            token = json.load(f)['token']
    except:
        raise AttributeError("Couldn't locate token in environment variables or token file")
prefix = "."
with open('characters.json', 'r') as f:
    all_characters = json.load(f)

class BotClient(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.active_characters = [player.Character.from_json(char) 
                                  for char in all_characters]
    
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

    async def handle_commands(self, command, arg:str, message:discord.Message):
        print(command, arg)
        
        if command == 'add':
            self.parse_player(message)
        if command == 'roll':
            char, _ = self.get_character(message.author)
            
            skill, prof, adv, name = self.parse_roll(arg)
            
            rolls, result = char.roll_skill(char, skill, prof=prof, adv=adv)
            print(prof, adv)
            action_display = f'Rolled {name} for {message.author.mention} : `{rolls}` with result **{result}**'
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
            # 
            _, index = self.get_character(message.author)
            skill = roll_module.skills[roll_module.autocomplete(arg[0], roll_module.skills)]

            # make sure a regular stat was entered
            if skill not in roll_module.stats:
                action_display = f"Cannot set {arg[0]} on character!"
                await message.channel.send(action_display)
                return

            # make sure the following argument is an int
            try:
                setto = int(arg[1])
            except:
                action_display = f"Cannot set {skill} to {arg[1]}!"
                await message.channel.send(action_display)
                return

            print(f"skill: {skill}, setto: {setto}")
            self.active_characters[index].stats[skill] = setto
            print(self.active_characters[index].stats)



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

    def get_character(self, owner : str) -> player.Character:
        for c, char in enumerate(self.active_characters):
            if char.owner == str(owner):
                return char, c
        return None

    def save_json(self):
        all_characters = [char.to_json() for char in self.active_characters]
        print()
        with open("characters.json", 'w') as f:
            json.dump(all_characters, f, indent=2)

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
        
        parsed = argparser.parse(message, args, kwargs) 
        # sort out namespace error, with str and int
        parsed['_str'] = parsed.pop('str')
        parsed['_int'] = parsed.pop('int')
        
        print(parsed, type(parsed))
        # pylint: disable=unexpected-keyword-arg
        char = player.Character(**parsed)
        char.set_owner(message.author)
        self.active_characters.append(char)
        self.save_json()

    def parse_roll(self, arg):
        
        call_skil = roll_module.autocomplete(arg[0], roll_module.skills)
        skill = roll_module.skills[call_skil]

        if len(arg) > 1:
            appendage = arg[1]
            prof = min(appendage.count("+"), 2)
            if   "x" in appendage:
                adv = 1
            elif "d" in appendage:
                adv = -1
            else:
                adv = 0
        else:
            prof = 0
            adv = 0

        return skill, prof, adv, call_skil



def main():
    global client
    try:
        client = BotClient()
        client.run(token)
    finally:
        client.save_json()

if __name__ == '__main__':
    main()
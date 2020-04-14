"""
discord bot to handle rerolls for characters in DnD
"""
import discord, os, json
import argparser, player

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

        if command.startswith("add"):
            
            self.parse_player(command[len('add')+len(prefix):])


    def save_json(self):
        all_characters = [char.to_json() for char in self.active_characters]
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

        # sort
        parsed['_str'] = parsed.pop('str')
        parsed['_int'] = parsed.pop('int')
        
        # pylint: disable=unexpected-keyword-arg
        char = player.Character(**parsed)
        char.set_owner(message.author)
        self.active_characters.append(char)



def main():
    global client
    try:
        client = BotClient()
        #client.run(token)
    finally:
        client.save_json()

if __name__ == '__main__':
    main()
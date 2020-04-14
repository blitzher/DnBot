"""
discord bot to handle rerolls for characters in DnD
"""
import discord, os, dotenv
import argparser, player

token = os.getenv('DISCORD')
prefix = "."

class BotClient(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        active_characters = []
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord')

    def handle_command(self, command):
        pass

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return # Don't respond to own messages
        
        if message.content.startswith('.'):
            command = message.content[1:]

        if command.startswith("add"):
            
            char = self.parse_player(command[len('add')+len(prefix):])

            await message.channel.send(char)


    def parse_player(self, message : discord.Message):
        args = ('level','name')
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
        return char









def main():
    client = BotClient()
    client.run(token)

if __name__ == '__main__':
    main()
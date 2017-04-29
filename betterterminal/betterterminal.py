from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import pagify, box
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from os.path import expanduser, exists
from os import makedirs


class BetterTerminal:
    """repl like Terminal in discord"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/betterterminal/settings.json')
        self.prefix = self.settings['prefix']
        self.sessions = []

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def cmd(self, ctx):

        if ctx.message.channel.id in self.sessions:
            await self.bot.say('Already running a BetteTerminal session in this channel. Exit it with `quit`')
            return

        self.sessions.append(ctx.message.channel.id)
        await self.bot.say('Enter commands after {} to execute them. ``exit()` or `quit` to exit.'.format(self.prefix))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def cmdsettings(self, ctx):
        """Settings for BetterTerminal"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @cmdsettings.command(name="prefix", pass_context=True)
    async def _prefix(self, ctx, prefix:str):
        """Set the prefix for the Terminal"""

        self.prefix = prefix
        self.settings['prefix'] = self.prefix
        dataIO.save_json('data/betterterminal/settings.json', self.settings)
        await self.bot.say('`Changed max search results to {} `'.format(self.prefix))

    async def on_message(self, message):

        if message.channel.id in self.sessions:


            if not self.prefix:
                check_folder()
                check_file()

            if message.content.startswith(self.prefix) and message.author.id == self.bot.settings.owner:
                command = message.content.split(self.prefix)[1]

                if command == 'exit()' or command == 'quit':
                    await self.bot.send_message(message.channel, 'Exiting.')
                    self.sessions.remove(message.channel.id)
                    return

                if command.lower().find("apt-get install") != -1 and command.lower().find("-y") == -1:
                    command = "{} -y".format(command)

                try:
                    output = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0]
                    error = False
                except CalledProcessError as e:
                    output = e.output
                    error = True

                shell = output.decode('utf_8')

                if shell == "" and not error:
                    return

                for page in pagify(shell, shorten_by=20):
                    await self.bot.send_message(message.channel, box(page, 'Prolog'))


def check_folder():
    if not exists("data/betterterminal"):
        print("[Terminal]Creating data/betterterminal folder...")
        makedirs("data/betterterminal")


def check_file():
    if not dataIO.is_valid_json("data/betterterminal/settings.json"):
        print("[BetterTerminal]Creating default whitelist.json...")
        dataIO.save_json("data/betterterminal/settings.json", {"prefix":">"})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(BetterTerminal(bot))
import discord
from discord.ext import commands
import config, asyncio

#import all of the cogs
from help_cog import help_cog
from music import music
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

#remove the default help command so that we can write out own
bot.remove_command('help')

async def main():
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(music(bot))
        await bot.start(config.TOKEN)

asyncio.run(main())
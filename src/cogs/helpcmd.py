import json
import discord
from discord.ext import commands

with open("./config.json", "r") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
bot_server = data["bot"]["server"]


class HelpCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="help", description="Get help for commands of the bot."
    )
    async def help(self, ctx):
        embed = discord.Embed(title="Help Menu:", color=int(embed_color[1:], 16))
        embed.add_field(
            name="Commands:",
            value=f"```{', '.join(c.name for c in self.bot.commands)}```",
            inline=False,
        )
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Support Server",
                url=bot_server,
            )
        )
        await ctx.respond(embed=embed, view=view)


def setup(bot):
    bot.add_cog(HelpCmd(bot))

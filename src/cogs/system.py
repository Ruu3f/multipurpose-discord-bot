import json, time, psutil, discord
from discord.ext import commands

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]
bot_server = data["bot"]["server"]
bot_version = data["bot"]["version"]
bot_author = data["bot"]["author"]


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    bot = discord.commands.SlashCommandGroup("bot")

    @bot.command(name="help", description="Get help for commands of the bot.")
    async def help(self, ctx):
        embed = discord.Embed(title="Help Menu:", color=int(embed_color[1:], 16))
        embed.add_field(
            name="Fun",
            value="```/fun quiz, /fun 8ball, /fun sudo, /fun slots, /fun rate, /fun iq, /fun dice, /fun hack, /fun fact, /fun meme, /fun coinflip, /fun showerthoughts, /fun wouldyourather.```",
            inline=False,
        )
        embed.add_field(
            name="Utility",
            value="```/utility purge, /utility slowmode, /utility avatar, /utility banner, /utility lock, /utility unlock, /utility mcinfo, /utility serverinfo, /utility userinfo, /utility nuke, /utility nick, /utility emojiurl.```",
            inline=False,
        )
        embed.add_field(
            name="Moderation",
            value="```/moderate timeout, /moderate untimeout, /moderate ban, /moderate kick, /moderate vkick, /moderate move, /moderate role, /automod swearfilter, /automod capsfilter, /automod linkblocker.```",
            inline=False,
        )
        embed.add_field(
            name="Text",
            value="```/text double, /text encode, /text decode, /text reverse, /text capitalize.```",
        )
        embed.add_field(
            name="System",
            value="```/bot ping, /bot uptime, /bot stats, /bot help.```",
            inline=False,
        )
        embed.add_field(
            name="Automatic",
            value="```/automeme setup, /automeme reset, /chatbot setup, /chatbot reset.```",
            inline=False,
        )
        embed.set_footer(text=f"Version: {bot_version}")

        button1 = discord.ui.Button(
            label="Invite me",
            url="None",
        )
        button2 = discord.ui.Button(
            label="Support Server",
            url=bot_server,
        )
        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.respond(embed=embed, view=view)

    @bot.command(name="uptime", description="See the uptime of the bot.")
    async def uptime(self, ctx):
        proc = psutil.Process()
        with proc.oneshot():
            uptime = time.time() - proc.create_time()
            uptime_formatted = f"{int(uptime // 86400)} days, {int(uptime // 3600 % 24)} hours, {int(uptime // 60 % 60)} minutes, {int(uptime % 60)} seconds"
            embed = discord.Embed(
                description=uptime_formatted, color=int(embed_color[1:], 16)
            )
            await ctx.respond(embed=embed)

    @bot.command(name="ping", description="Get a pong message with response time.")
    async def ping(self, ctx):
        embed = discord.Embed(
            description=f"Pong! {self.bot.latency*1000:.2f}ms",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @bot.command(name="stats", description="Show's the bot's current stats.")
    async def stats(self, ctx):
        embed = discord.Embed(title="Bot Stats", color=int(embed_color[1:], 16))
        embed.add_field(name="Owner:", value=self.bot.get_user(int(bot_author)).mention)
        embed.add_field(name="Bot Version:", value=bot_version)
        embed.add_field(name="Shards:", value=self.bot.shard_count)
        embed.add_field(name="Servers:", value=len(self.bot.guilds))
        embed.add_field(
            name="Channels:",
            value=sum(len(guild.channels) for guild in self.bot.guilds),
        )
        embed.add_field(
            name="Members:", value=sum(len(guild.members) for guild in self.bot.guilds)
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(System(bot))

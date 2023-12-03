import json
import time
import psutil
import aiohttp
import discord
from discord.ext import commands

with open("./config.json", "r") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
failed_emoji = data["emoji"]["failed"]


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    info = discord.commands.SlashCommandGroup("info")

    @info.command(
        name="membercount",
        description="View the count and total count of members and bots of this server.",
    )
    async def membercount(self, ctx):
        guild = ctx.guild
        bot_count = len([m for m in guild.members if m.bot])
        member_count = guild.member_count - bot_count
        total_count = member_count + bot_count
        embed = discord.Embed(title="Counts:", color=int(embed_color[1:], 16))
        embed.add_field(name="Members:", value=member_count)
        embed.add_field(name="Bots:", value=bot_count)
        embed.add_field(name="Total:", value=total_count)
        await ctx.respond(embed=embed)

    @info.command(name="server", description="Information about this server.")
    async def server(self, ctx):
        guild = ctx.guild
        creation_timestamp = guild.created_at.strftime("%d.%m.%y")
        embed = discord.Embed(
            title="Server Information:",
            description="Here is some information about the server:",
            color=int(embed_color[1:], 16),
        )
        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name=guild.name)
        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Server Owner", value=guild.owner, inline=True)
        embed.add_field(name="Server Member Count", value=guild.member_count)
        embed.add_field(name="Category Channels", value=len(guild.categories))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Members", value=len(guild.members))
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"ID: {guild.id} | Server created {creation_timestamp}")
        await ctx.respond(embed=embed)

    @info.command(name="user", description="Information about a user.")
    async def user(
        self,
        ctx,
        user: discord.commands.Option(
            discord.Member, "The member to get the information of.", required=True
        ),
    ):
        roles = ", ".join([role.mention for role in user.roles[1:]])
        joined_at_unix = int(user.joined_at.timestamp())
        joined_at_timestamp = f"<t:{joined_at_unix}:f>"
        created_at_unix = int(user.created_at.timestamp())
        created_at_timestamp = f"<t:{created_at_unix}:f>"
        embed = discord.Embed(title="User Information:", color=int(embed_color[1:], 16))
        if user.avatar:
            embed.set_author(name=user.name, icon_url=user.avatar.url)
        else:
            embed.set_author(name=user.name)
        embed.add_field(name="Roles", value=roles, inline=False)
        embed.add_field(name="Joined", value=joined_at_timestamp, inline=True)
        embed.add_field(name="Created", value=created_at_timestamp, inline=True)
        embed.set_footer(text=f"ID: {user.id}")
        await ctx.respond(embed=embed)

    @info.command(
        name="minecraft", description="See information of a minecraft server."
    )
    async def minecraft(
        self,
        ctx,
        ip: discord.commands.Option(
            str, "Put the server ip and port to see the status of it.", required=True
        ),
    ):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.mcsrvstat.us/2/{ip}", timeout=5
                ) as resp:
                    response = await resp.json()
            status = "+ | Online"
        except (aiohttp.ClientError, json.JSONDecodeError):
            status = "- | Offline"
        players = response.get("players", {}).get("online", 0)
        version = response.get("version", "N/A")

        try:
            embed = discord.Embed(
                title="MC Server Info:", color=int(embed_color[1:], 16)
            )
            embed.add_field(name="IP:", value=f"```yaml\n{ip}```", inline=False)
            embed.add_field(name="Status:", value=f"```diff\n{status}```", inline=False)
            embed.add_field(
                name="Version:", value=f"```elm\n{version}```", inline=False
            )
            embed.add_field(
                name="Players Online:", value=f"```apache\n{players}```", inline=False
            )
            await ctx.respond(embed=embed)
        except Exception:
            await ctx.respond(
                f"{failed_emoji} There was an error while trying to get the server info."
            )

    @info.command(name="avatar", description="Get your/other's avatar.")
    async def avatar(
        self,
        ctx,
        *,
        user: discord.commands.Option(
            discord.Member, "The member to get the avatar of.", required=True
        ),
    ):
        embed = discord.Embed(
            title=f"{user.name}'s avatar:", color=int(embed_color[1:], 16)
        )
        embed.set_image(url=user.avatar.url)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Download", url=user.avatar.url))
        await ctx.respond(embed=embed, view=view)

    @info.command(name="banner", description="Get your/other's banner.")
    async def banner(
        self,
        ctx,
        *,
        user: discord.commands.Option(
            discord.Member, "The member to get the banner of.", required=True
        ),
    ):
        if user.banner:
            embed = discord.Embed(
                title=f"{user.name}'s banner:", color=int(embed_color[1:], 16)
            )
            embed.set_image(url=user.banner.url)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Download", url=user.banner.url))
            await ctx.respond(embed=embed, view=view)
        else:
            await ctx.respond("This user does not have a banner.")

    @info.command(name="botstats", description="Show's the bot's current stats.")
    async def stats(self, ctx):
        embed = discord.Embed(title="Bot Stats", color=int(embed_color[1:], 16))
        embed.add_field(name="Latency:", value=f"{self.bot.latency*1000:.2f}ms")
        process = psutil.Process()
        with process.oneshot():
            uptime = int(time.time() - process.create_time())
            embed.add_field(
                name="Uptime:",
                value=f"{int(uptime // 86400)}d, {int(uptime // 3600 % 24)}h, {int(uptime // 60 % 60)}m, {int(uptime % 60)}s",
            )
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
    bot.add_cog(Info(bot))

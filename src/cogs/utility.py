import json, discord
from discord.ext import commands

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    util = discord.commands.SlashCommandGroup("utility")

    @util.command(name="poll", description="Create a poll to vote an item.")
    @commands.has_permissions(manage_messages=True)
    async def poll(
        self,
        ctx,
        item: discord.commands.Option(
            str, "Put the thing you want to poll for.", required=True
        ),
    ):
        embed = discord.Embed(
            title="Poll time!", description=f"{item}", color=int(embed_color[1:], 16)
        )
        poll = await ctx.respond(embed=embed)
        await poll.add_reaction("🔺")
        await poll.add_reaction("🔻")

    @util.command(name="purge", description="Purge messages.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(
        self,
        ctx,
        amount: discord.commands.Option(
            int, "Put how many message you want to purge.", required=True
        ),
    ):
        await ctx.defer()
        if amount > 1000:
            await ctx.respond(
                f"{failed_emoji} You cannot purge more than 1000 messages at a time.",
                ephemeral=True,
            )
            return
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{success_emoji} Messages purged:",
            description=f"{len(deleted)} messages have been purged.",
            color=int(embed_color[1:], 16),
        )
        await ctx.send(embed=embed, delete_after=5)

    @util.command(name="clear", description="Clear messages.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx,
        amount: discord.commands.Option(
            int, "Put how many message you want to clear.", required=True
        ),
    ):
        await ctx.defer()
        if amount > 1000:
            await ctx.respond(
                f"{failed_emoji} You cannot clear more than 1000 messages at a time.",
                ephemeral=True,
            )
            return
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{success_emoji} Messages cleared:",
            description=f"{len(deleted)} messages have been cleared.",
            color=int(embed_color[1:], 16),
        )
        await ctx.send(embed=embed, delete_after=5)

    @util.command(
        name="slowmode", description="Sets the slowmode for the current channel."
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx,
        duration: discord.commands.Option(
            str, "Put something like 1s, 1m or 1h here.", required=True
        ),
    ):
        if "s" in duration:
            time = int(duration.replace("s", ""))
        elif "m" in duration:
            time = int(duration.replace("m", "")) * 60
        elif "h" in duration:
            time = int(duration.replace("h", "")) * 3600
        else:
            return await ctx.respond(
                f"{failed_emoji} Invalid duration format. Use a format like: 1s, 1m, or 1h."
            )

        await ctx.channel.edit(slowmode_delay=time)
        await ctx.respond(f"{success_emoji} Slowmode set for {duration}.")

    @util.command(name="nick", description="Change a user's nickname.")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(
        self,
        ctx,
        *,
        user: discord.commands.Option(
            discord.Member, "The member to change the nickname of.", required=True
        ),
        nickname: discord.commands.Option(
            str, "The nickname you want to set to the user you put.", required=True
        ),
    ):
        if user:
            member = user
        else:
            member = ctx.user
        await member.edit(nick=nickname)
        await ctx.respond(
            f"<:tick:1070361257200324680> Successfully changed {member}'s nickname to {nickname}."
        )

    @util.command(name="nuke", description="Nuke the current channel.")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        channel = ctx.channel
        position = channel.position
        await channel.delete()
        new_channel = await channel.clone(reason="Nuked")
        await new_channel.edit(position=position)
        embed = discord.Embed(
            title="Channel nuked!",
            description=f"Nuked by {ctx.author.mention}",
            color=int(embed_color[1:], 16),
        )
        embed.set_image(
            url="https://media.giphy.com/media/hvGKQL8lasDvIlWRBC/giphy.gif"
        )
        await new_channel.send(embed=embed)

    @util.command(
        name="emojiurl", description="Get the url of a specified custom emoji."
    )
    async def emojiurl(
        self,
        ctx,
        emoji: discord.commands.Option(
            discord.Emoji, "The field to put the emoji in.", required=True
        ),
    ):
        emoji_url = str(emoji.url)
        embed = discord.Embed(
            title=f"{emoji} Emoji URL",
            description=emoji_url,
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @util.command(name="lock", description="Lock the current channel.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.respond(f"{success_emoji} {ctx.channel.mention} has been locked.")

    @util.command(name="unlock", description="Unlock the current channel.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.respond(f"{success_emoji} {ctx.channel.mention} has been unlocked.")


def setup(bot):
    bot.add_cog(Utility(bot))

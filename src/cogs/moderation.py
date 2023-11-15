import json, discord
from discord.ext import commands

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mod = discord.commands.SlashCommandGroup("moderate")

    @mod.command(name="ban", description="Punish users.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.commands.Option(
            discord.Member, "The member to punish.", required=True
        ),
        reason: discord.commands.Option(
            str, "The reason of punishing.", required=False
        ),
    ):
        if ctx.author.top_role <= member.top_role:
            await ctx.respond(
                f"{failed_emoji} Can't ban this user because your role is equal to or lower than their role.",
                ephemeral=True,
            )
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.respond(
                f"{failed_emoji} Can't ban this user because my role is below the user's highest role.",
                ephemeral=True,
            )
            return
        if not reason:
            reason = "No reason provided."
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(
            title=f"{success_emoji} User Banned",
            description=f"{member.mention} has been banned with reason: `{reason}`.",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)
        await member.send(
            f"You have been banned from `{ctx.guild}` with reason: {reason}"
        )

    @mod.command(name="kick", description="Punish users.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: discord.commands.Option(
            discord.Member, "The member to punish.", required=True
        ),
        reason: discord.commands.Option(
            str, "The reason of punishing.", required=False
        ),
    ):
        if ctx.author.top_role <= member.top_role:
            await ctx.respond(
                f"{failed_emoji} Can't kick this user because your role is equal to or lower than their role.",
                ephemeral=True,
            )
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.respond(
                f"{failed_emoji} Can't kick this user because my role is below the user's highest role.",
                ephemeral=True,
            )
            return
        if not reason:
            reason = "No reason provided."
        await ctx.guild.kick(member, reason=reason)
        embed = discord.Embed(
            title=f"{success_emoji} User kicked",
            description=f"{member.mention} has been kicked with reason: `{reason}`.",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)
        await member.send(
            f"You have been kicked from `{ctx.guild}` with reason: {reason}"
        )

    @mod.command(name="mute", description="Mute a user.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(
        self,
        ctx,
        member: discord.commands.Option(
            discord.Member, "The member to punish.", required=True
        ),
        duration: discord.commands.Option(
            str, "Put something like 1s, 1m, 1h or 1d here.", required=True
        ),
        reason: discord.commands.Option(
            str, "The reason of punishing.", required=False
        ),
    ):
        if duration is None:
            await ctx.respond(f"{failed_emoji} Please provide a valid duration.")
            return

        if reason is None:
            reason = "No reason provided."

        time_suffixes = {"m": 60, "h": 3600, "d": 86400}
        if duration[:-1].isdigit() and duration[-1] in time_suffixes:
            time = int(duration[:-1]) * time_suffixes[duration[-1]]
            if time >= 86400:
                duration_string = f"{time // 86400} day(s)"
            elif time >= 3600:
                duration_string = f"{time // 3600} hour(s)"
            elif time >= 60:
                duration_string = f"{time // 60} minute(s)"
            else:
                duration_string = f"{time} second(s)"
        await member.timeout_for(duration=time, reason=reason)
        embed = discord.Embed(
            description=f"{success_emoji} {member.mention} has been muted for {duration_string} by {ctx.author.mention}.\nReason: {reason}",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @mod.command(name="unmute", description="Unmute a user.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(
        self,
        ctx,
        member: discord.commands.Option(
            discord.Member, "The member to punish.", required=True
        ),
    ):
        if member == ctx.author:
            embed = discord.Embed(
                description="You cannot unmute yourself.",
                color=int(embed_color[1:], 16),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        await member.remove_timeout()
        embed = discord.Embed(
            description=f"{success_emoji} {member.mention} has been unmuted by {ctx.author.mention}.",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))

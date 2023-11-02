import re, json, aiohttp, random, discord, datetime
from discord.ext import commands, tasks

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]


class Automatic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False
        self.cf_enabled = {}
        self.lf_enabled = {}
        self.sf_enabled = {}
        self.ap_enabled = {}

    chatbot = discord.commands.SlashCommandGroup("chatbot")

    @chatbot.command(name="setup", description="Setup the chatbot.")
    @commands.has_permissions(manage_channels=True)
    async def chatbot_setup(self, ctx, channel):
        await ctx.defer()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM datastorage WHERE guilds = ?", (ctx.guild.id,)
            )
            data = await cursor.fetchone()
            if not data:
                await cursor.execute(
                    "INSERT INTO datastorage VALUES (?,?,?)",
                    (
                        ctx.guild.id,
                        channel.id,
                        None,
                    ),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} Successfully set up the chatbot with channel {channel.mention}.",
                    ephemeral=True,
                )
            else:
                await cursor.execute(
                    "UPDATE datastorage SET chatbot_channels = ? WHERE guilds = ?",
                    (
                        channel.id,
                        ctx.guild.id,
                    ),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} Successfully updated the chatbot with channel {channel.mention}.",
                    ephemeral=True,
                )

    @chatbot.command(name="reset", description="Reset the chatbot.")
    @commands.has_permissions(manage_channels=True)
    async def chatbot_reset(self, ctx):
        await ctx.defer()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM datastorage WHERE guilds = ?", (ctx.guild.id,)
            )
            data = await cursor.fetchone()
            if not data:
                await ctx.respond(
                    f"{failed_emoji} The chatbot is not set up. Set up the chatbot by `/chatbot setup` to set it up.",
                    ephemeral=True,
                )
            else:
                await cursor.execute(
                    "UPDATE datastorage SET chatbot_channels = ? WHERE guilds = ?",
                    (
                        None,
                        ctx.guild.id,
                    ),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} All the chatbot settings has been reset.",
                    ephemeral=True,
                )

    automemes = discord.commands.SlashCommandGroup("automemes")

    @automemes.command(name="setup", description="Setup automemes.")
    @commands.has_permissions(manage_channels=True)
    async def automemes_setup(self, ctx, channel):
        await ctx.defer()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM datastorage WHERE guilds = ?", (ctx.guild.id,)
            )
            data = await cursor.fetchone()
            if not data:
                await cursor.execute(
                    "INSERT INTO datastorage VALUES (?,?,?)",
                    (ctx.guild.id, None, channel.id),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} Successfully set up automemes with channel {channel.mention}.",
                )
            else:
                await cursor.execute(
                    "UPDATE datastorage SET automeme_channels = ? WHERE guilds = ?",
                    (channel.id, ctx.guild.id),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} Successfully updated automemes to go in channel {channel.mention}.",
                    ephemeral=True,
                )

    @automemes.command(name="reset", description="Reset automemes.")
    @commands.has_permissions(manage_channels=True)
    async def automemes_reset(self, ctx):
        await ctx.defer()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM datastorage WHERE guilds = ?", (ctx.guild.id,)
            )
            data = await cursor.fetchone()
            if not data:
                await ctx.respond(
                    f"{failed_emoji} Automemes are not set up. Set them up by `/automemes setup` to set them up.",
                    ephemeral=True,
                )
            else:
                await cursor.execute(
                    "UPDATE datastorage SET automeme_channels = ? WHERE guilds = ?",
                    (None, ctx.guild.id),
                )
                await self.bot.db.commit()
                await ctx.respond(
                    f"{success_emoji} All the automemes settings has been reset.",
                    ephemeral=True,
                )

    automod = discord.commands.SlashCommandGroup("automod")

    @automod.command(
        name="capsfilter", description="Toggle caps filter module for your server."
    )
    async def capsfilter(self, ctx):
        guild_id = ctx.guild.id
        self.cf_enabled[guild_id] = not self.cf_enabled.get(guild_id, False)
        await ctx.respond(
            f"{success_emoji} Caps filter module {'enabled' if self.cf_enabled[guild_id] else 'disabled'}."
        )

    @automod.command(
        name="linkfilter", description="Toggle link filter module for your server."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def linkfilter(self, ctx):
        guild_id = ctx.guild.id
        self.lf_enabled[guild_id] = not self.lf_enabled.get(guild_id, False)
        await ctx.respond(
            f"{success_emoji} Link filter module {'enabled' if self.lf_enabled[guild_id] else 'disabled'}."
        )

    @automod.command(
        name="swearfilter", description="Toggle swear filter module for your server."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def swearfilter(self, ctx):
        guild_id = ctx.guild.id
        self.sf_enabled[guild_id] = not self.sf_enabled.get(guild_id, False)
        await ctx.respond(
            f"{success_emoji} Swear filter module {'enabled' if self.sf_enabled[guild_id] else 'disabled'}."
        )

    @automod.command(
        name="antighostping", description="Toggle antighostping module for your server."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def antighostping(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.ap_enabled:
            self.ap_enabled[guild_id] = not self.ap_enabled[guild_id]
        else:
            self.ap_enabled[guild_id] = True

        if self.ap_enabled[guild_id]:
            await ctx.respond(
                f"{success_emoji} Ghost ping detection is now enabled for this guild."
            )
        else:
            await ctx.respond(
                f"{success_emoji} Ghost ping detection is now disabled for this guild."
            )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.ready = True

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.ready:
            if message.author == self.bot.user:
                return
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM datastorage WHERE guilds = ?", (message.guild.id,)
                )
                data = await cursor.fetchone()
                if not data:
                    return
                else:
                    if message.channel.id == data[1]:
                        params = {
                            "bid": "",
                            "key": "",
                            "uid": message.author.id,
                            "msg": message.content,
                        }
                        async with aiohttp.ClientSession(
                            headers={"Authorization": ""}
                        ) as session:
                            async with session.get(
                                "http://api.brainshop.ai/get", params=params
                            ) as resp:
                                response = await resp.json()
                                await message.channel.send(response["cnt"])
        if message.guild.id in self.cf_enabled and self.cf_enabled[message.guild.id]:
            caps_count = sum(1 for c in message.content if c.isupper())
            if caps_count / len(message.content) > 0.75:
                await message.delete()
                await message.channel.send(
                    f"{failed_emoji} excessive caps are not allowed!",
                    delete_after=5,
                )
        if message.guild.id in self.sf_enabled and self.sf_enabled[message.guild.id]:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.purgomalum.com/service/containsprofanity?text={message.content}&censor=true"
                ) as resp:
                    if (await resp.text()) == "true":
                        await message.delete()
                        await message.channel.send(
                            f"{failed_emoji} please watch your language! Swearing is not allowed.",
                            delete_after=5,
                        )
        if message.guild.id in self.lf_enabled and self.lf_enabled[message.guild.id]:
            if re.search(r"(http|ftp|https):\/\/", message.content):
                await message.delete()
                await message.channel.send(
                    f"{failed_emoji} links are not allowed!",
                    delete_after=5,
                )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user or not message.mentions:
            return

        guild_id = message.guild.id
        if guild_id not in self.ap_enabled or not self.ap_enabled[guild_id]:
            return

        async for entry in message.guild.audit_logs(
            limit=1, action=discord.AuditLogAction.message_delete
        ):
            if (
                datetime.datetime.now(datetime.timezone.utc) - message.created_at
            ) < datetime.timedelta(minutes=5):
                embed = discord.Embed(
                    title="Ghost Ping Detected!",
                    description=f"{message.mentions[0].mention} got ghost pinged by {message.author.mention}.",
                    color=discord.Color.red(),
                )
                embed.add_field(
                    name="Message:", value=f"```{message.content}```", inline=False
                )
                embed.set_footer(
                    text=f"Today at {message.created_at.strftime('%I:%M %p')}"
                )
                await message.channel.send(embed=embed)
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM datastorage WHERE guilds = ?", (guild.id,)
            )
            data = await cursor.fetchone()
            if not data:
                pass
            else:
                await cursor.execute(
                    "UPDATE datastorage SET automeme_channels = ?, chatbot_channels = ? WHERE guilds = ?",
                    (
                        None,
                        None,
                        guild.id,
                    ),
                )
                await self.bot.db.commit()

    @tasks.loop(minutes=5, reconnect=True)
    async def send_automeme(self):
        if self.ready:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.reddit.com/r/memes.json") as r:
                    js = await r.json()
                    memes = [
                        post
                        for post in js["data"]["children"]
                        if not post["data"]["over_18"]
                    ]
                    random_meme = random.choice(memes)["data"]
                    embed = discord.Embed(
                        title=random_meme["title"], color=int(embed_color[1:], 16)
                    )
                    embed.set_author(
                        name=random_meme["author"],
                        url=f"https://reddit.com{random_meme['permalink']}",
                    )
                    embed.set_image(url=random_meme["url"])
                    embed.set_footer(
                        text=f"👍 {random_meme['ups']} | 💬 {random_meme['num_comments']}"
                    )
                    async with self.bot.db.cursor() as cursor:
                        await cursor.execute("SELECT * FROM datastorage")
                        data = await cursor.fetchall()
                        if not data:
                            return
                        for guild in data:
                            channel = self.bot.get_channel(guild[2])
                            if channel:
                                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Automatic(bot))

import os, json, asyncio, discord, aiosqlite
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]
bot_server = data["bot"]["server"]
bot_author = data["bot"]["author"]
bot_token = data["bot"]["token"]


class Bot(commands.Bot):
    def __init__(self):
        self.guild_command_usage = []
        super().__init__(
            intents=intents,
            help_command=None,
            auto_sync_commands=True,
        )
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"\033[1;32m INFO \033[0m| Loaded {filename}")
                except Exception as e:
                    print(
                        f"\033[1;31;40m INFO \033[0m| Failed to load {filename}\n\033[1;31;40m ---> \033[0m| {e}"
                    )

    async def on_ready(self):
        print(
            f"\033[1;94m INFO \033[0m| Logged in as {self.user.name}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        self.db = await aiosqlite.connect("./database.db")
        await asyncio.sleep(2)
        async with self.db.cursor() as cursor:
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS datastorage(guilds INTEGER, chatbot_channels INTEGER, automeme_channels INTEGER)"
            )
        while True:
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{len(self.guilds)} servers.",
                ),
            )
            await asyncio.sleep(300)

    async def on_message(self, msg):
        if msg.content == f"<@{self.user.id}>":
            await msg.add_reaction("👀")

    async def on_application_command_error(self, ctx, err):
        embed = discord.Embed(
            description=f"{failed_emoji} {str(err)}", color=int(embed_color[1:], 16)
        )
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Report this error",
                url=bot_server,
                emoji=f"{success_emoji}",
            )
        )
        await ctx.respond(embed=embed, view=view, ephemeral=True)


if __name__ == "__main__":
    asyncio.run(Bot().run(bot_token))

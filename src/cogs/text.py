import base64
import codecs
import discord
from discord.ext import commands


class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    text = discord.commands.SlashCommandGroup("text")

    @text.command(
        name="double",
        description="Enter your text to convert it to double text (`lliikkee tthhiiss`).",
    )
    async def double(
        self, ctx, *, text: discord.commands.Option(str, "Your text", required=True)
    ):
        await ctx.respond("".join([char * 2 for char in text]))

    @text.command(
        name="encode",
        description="Enter your text to encode it.",
    )
    async def encode(
        self, ctx, *, text: discord.commands.Option(str, "Your text.", required=True)
    ):
        encoded_text = (
            base64.b64encode(codecs.encode(text, "rot_13").encode())
            .decode()
            .replace("=", "")
        )
        await ctx.respond(encoded_text, ephemeral=True)

    @text.command(name="decode", description="Enter your encoded text to decode it.")
    async def decode(
        self,
        ctx,
        *,
        encoded_text: discord.commands.Option(str, "Your encoded code.", required=True),
    ):
        decoded_text = codecs.decode(
            base64.b64decode(
                encoded_text + "=" * (4 - (len(encoded_text) % 4))
            ).decode(),
            "rot_13",
        )
        await ctx.respond(decoded_text)

    @text.command(
        name="reverse", description="Enter your text to reverse it (`ekil siht`)."
    )
    async def reverse(
        self, ctx, *, text: discord.commands.Option(str, "Your text.", required=True)
    ):
        await ctx.respond(text[::-1])

    @text.command(
        name="capitalize", description="Enter your text to capitalize it (`Like This`)."
    )
    async def capitalize(
        self, ctx, *, text: discord.commands.Option(str, "Your text.", required=True)
    ):
        await ctx.respond(text.title())

    @text.command(
        name="countletters",
        description="Enter your text to count the number of letters in it.",
    )
    async def countletters(
        self, ctx, *, text: discord.commands.Option(str, "Your text.", required=True)
    ):
        await ctx.respond(
            f"The text contains {sum(1 for char in text if char.isalpha())} letters."
        )

    @text.command(
        name="lowercase", description="Enter your text to convert it to lowercase."
    )
    async def lowercase(
        self, ctx, *, text: discord.commands.Option(str, "Your text.", required=True)
    ):
        await ctx.respond(text.lower())


def setup(bot):
    bot.add_cog(Text(bot))

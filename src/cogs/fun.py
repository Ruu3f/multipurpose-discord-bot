import json, html, string, random, aiohttp, discord
from discord.ext import commands

with open("./config.json") as f:
    data = json.load(f)

embed_color = data["misc"]["embed_color"]
success_emoji = data["emoji"]["success"]
failed_emoji = data["emoji"]["failed"]


class QuizView(discord.ui.View):
    def __init__(self, question, options, correct_answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

        for option in options:
            if option == correct_answer:
                button = QuizButton(
                    label=option, custom_id=option, disabled=False, row=1
                )
                button.correct = True
            else:
                button = QuizButton(
                    label=option, custom_id=option, disabled=False, row=1
                )
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        selected_option = interaction.data["custom_id"]
        correct_button = next(button for button in self.children if button.correct)
        correct_option = correct_button.custom_id

        if selected_option == correct_option:
            for item in self.children:
                item.disabled = True
                if isinstance(item, QuizButton):
                    if item.custom_id == selected_option:
                        item.style = discord.ButtonStyle.green
                    else:
                        item.style = discord.ButtonStyle.gray
            await interaction.response.send_message(f"{success_emoji} Correct!")
        else:
            for item in self.children:
                item.disabled = True
                if isinstance(item, QuizButton):
                    if item.custom_id == selected_option:
                        item.style = discord.ButtonStyle.red
                    elif item.correct:
                        item.style = discord.ButtonStyle.green
                    else:
                        item.style = discord.ButtonStyle.gray
            await interaction.response.send_message(
                f"{failed_emoji} Wrong! The correct answer was {self.correct_answer}."
            )

        await interaction.message.edit(view=self)
        return False


class QuizButton(discord.ui.Button):
    def __init__(self, label, custom_id, **kwargs):
        super().__init__(label=label, custom_id=custom_id, **kwargs)
        self.correct = False

    async def callback(self, interaction: discord.Interaction):
        await self.view.interaction_check(interaction, self.correct)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    fun = discord.commands.SlashCommandGroup("fun")

    @fun.command(name="coinflip", description="Flip a coin!")
    async def coinflip(self, ctx):
        outcomes = ["Heads", "Tails"]

        embed = discord.Embed(
            title="Coinflip!",
            description=f"Result: **{random.choice(outcomes)}**",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @fun.command(name="dice", description="Roll a dice!")
    async def dice(self, ctx):
        embed = discord.Embed(
            title="Dice!",
            description=f"You rolled a **{random.randint(1, 6)}**",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @fun.command(
        name="slots",
        description="Play a game of slots; it's random sometimes you can win and sometimes lose.",
    )
    async def slots(self, ctx):
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        slotmachine = f"[ {a} {b} {c} ]\n{ctx.author.mention}"
        if a == b == c:
            await ctx.respond(
                embed=discord.Embed(
                    title="Slot machine",
                    description=f"{slotmachine} All Matching! You Won!",
                    color=int(embed_color[1:], 16),
                )
            )
        elif (a == b) or (a == c) or (b == c):
            await ctx.respond(
                embed=discord.Embed(
                    title="Slot machine",
                    description=f"{slotmachine} 2 Matching! You Won!",
                    color=int(embed_color[1:], 16),
                )
            )
        else:
            await ctx.respond(
                embed=discord.Embed(
                    title="Slot machine",
                    description=f"{slotmachine} No Matches! You Lost!",
                    color=int(embed_color[1:], 16),
                )
            )

    @fun.command(
        name="iq",
        description="A fun command that generates a random amount of percentage.",
    )
    async def iq(
        self,
        ctx,
        user: discord.commands.Option(
            discord.Member,
            description="Choose a user to use the command on.",
            required=False,
        ),
    ):
        await ctx.defer()
        if not user:
            user = ctx.author
        embed = discord.Embed(
            description=f"{user.mention} has {random.randint(20, 200)} IQ 🧠",
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @fun.command(name="hack", description="A fun command that generates random values.")
    async def hack(
        self,
        ctx,
        user: discord.commands.Option(
            discord.Member, "The user whom you wish to use the command on."
        ),
    ):
        message = await ctx.respond("Hacking in progress...")
        await message.edit_original_response(
            content=f"{success_emoji} Successfully hacked {user.mention}"
        )
        embed = discord.Embed(
            title="Hack Results",
            description="Here are the results of the hack:",
            color=int(embed_color[1:], 16),
        )
        embed.add_field(name="Username", value=f"`{user.name}`", inline=True)
        embed.add_field(
            name="Password",
            value=f"||{''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12)).replace('|', '')}||",
            inline=True,
        )
        await ctx.send(embed=embed)

    @fun.command(
        name="8ball", description="Ask 8Ball a question and it will reply to that."
    )
    async def eightball(
        self,
        ctx,
        *,
        question: discord.commands.Option(
            str, "The field to put the question in.", required=True
        ),
    ):
        choices = [
            "yes",
            "no",
            "idk",
            "probably",
            "probably not",
            "can be true",
            "can be false",
        ]
        choice = random.choice(choices)
        embed = discord.Embed(title="🔮 8Ball", color=int(embed_color[1:], 16))
        if ctx.author.avatar:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=ctx.author.name)
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="8Ball says:", value=choice, inline=False)
        embed.set_footer(
            text="Note: This is 100% NOT accurate, you should not follow adviceses from it."
        )
        await ctx.respond(embed=embed)

    @fun.command(name="dadjoke", description="Get a random dad joke.")
    async def dadjoke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/slack") as resp:
                data = await resp.json()
                joke = data["attachments"][0]["text"]
                embed = discord.Embed(description=joke, color=int(embed_color[1:], 16))
                await ctx.respond(embed=embed)

    @fun.command(
        name="wouldyourather", description="Get a random would you rather question."
    )
    async def wouldyourather(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.popcat.xyz/wyr") as resp:
                question = await resp.json()
        embed = discord.Embed(title="Would You Rather:", color=int(embed_color[1:], 16))
        embed.add_field(name="", value=question["ops1"], inline=False)
        embed.add_field(name="", value="OR", inline=False)
        embed.add_field(name="", value=question["ops2"], inline=False)
        await ctx.respond(embed=embed)

    @fun.command(name="fact", description="Get a random fact.")
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.popcat.xyz/fact") as resp:
                fact = await resp.json()
        embed = discord.Embed(description=fact["fact"], color=int(embed_color[1:], 16))
        await ctx.respond(embed=embed)

    @fun.command(name="meme", description="Sends a random meme.")
    async def meme(self, ctx):
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.reddit.com/r/memes/hot.json?limit=100", headers=headers
            ) as resp:
                js = await resp.json()
        posts = js["data"]["children"]
        post = None
        while not post or post["data"]["over_18"]:
            post = posts[random.randint(0, len(posts) - 1)]
        embed = discord.Embed(
            title=post["data"]["title"], color=int(embed_color[1:], 16)
        )
        embed.set_author(
            name="r/memes",
            url=f"https://www.reddit.com{post['data']['permalink']}",
        )
        embed.set_image(url=post["data"]["url"])
        embed.set_footer(
            text=f"👍 {post['data']['ups']} | 💬 {post['data']['num_comments']}"
        )
        await ctx.respond(embed=embed)

    @fun.command(name="showerthoughts", description="Get a random shower thought.")
    async def showerthoughts(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.popcat.xyz/showerthoughts") as resp:
                data = await resp.json()
        result = data["result"]
        embed = discord.Embed(
            title="Random shower thought",
            description=result,
            color=int(embed_color[1:], 16),
        )
        await ctx.respond(embed=embed)

    @fun.command(
        name="quiz", description="Sends a four option quiz or a true false question."
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def quiz(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://opentdb.com/api.php?amount=1") as resp:
                data = (await resp.json())["results"][0]
        question = html.unescape(data["question"])
        correct_answer = html.unescape(data["correct_answer"])
        options = [html.unescape(answer) for answer in data["incorrect_answers"]] + [
            correct_answer
        ]
        random.shuffle(options)

        view = QuizView(
            question=question, options=options, correct_answer=correct_answer
        )
        embed = discord.Embed(
            description=f"**Question:** {question}", color=int(embed_color[1:], 16)
        )
        await ctx.respond(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Fun(bot))

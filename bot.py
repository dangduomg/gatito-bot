"""gatito-bot 2.0"""


import os
import random
import asyncio

import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])  # type: ignore

genai_model = genai.GenerativeModel()  # type: ignore

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


@bot.hybrid_command()
async def hello(ctx: commands.Context) -> None:
    """Says hello"""
    await ctx.send(f"Hello {ctx.author.mention}!")


@bot.hybrid_command()
async def dice(
    ctx: commands.Context,
    times: int = commands.param(
        description="The number of times the dice is rolled (1-100)",
        default=1
    ),
    sides: int = commands.param(
        description="The number of sides of the dice (2-100)", default=6
    ),
) -> None:
    """Rolls dices

Generates a random number from 1 to 6 by default."""

    if not 1 <= times <= 100:
        await ctx.send(
            "Please enter a valid number for the number of times (1-100)"
        )
        return
    if not 2 <= sides <= 100:
        await ctx.send(
            "Please enter a valid number for the number of sides (2-100)"
        )
        return

    rolls = [str(random.randint(1, sides)) for _ in range(times)]
    await ctx.send(' '.join(rolls))


@bot.hybrid_command()
async def lottery(
    ctx: commands.Context,
    numbers: int = commands.param(
        description="The number of numbers to generate (1-10)", default=6
    ),
    range_: int = commands.param(
        description="The range of numbers to generate (1-100)", default=6
    ),
) -> None:
    """Play the lottery

Generates a sequence of random numbers and asks the user to guess them."""

    if not 1 <= numbers <= 10:
        await ctx.send(
            "Please enter a valid number for the number of numbers (1-10)"
        )
        return

    if not 1 <= range_ <= 100:
        await ctx.send(
            "Please enter a valid number for the range of numbers (1-100)"
        )
        return

    correct_nums = [str(random.randint(1, range_)) for _ in range(numbers)]

    await ctx.send(
        "Please enter your sequence (You have 30 seconds to respond):"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond")
        return

    user_nums = msg.content.split()

    if len(user_nums) != numbers:
        await ctx.send(f"Please enter {numbers} numbers")
        return

    if user_nums != correct_nums:
        await ctx.send(f"The correct sequence is: {" ".join(correct_nums)}")
        await ctx.send("You didn't win this time! Good luck next time!")
        return

    await ctx.send("Congratulations! You won the lottery :tada::tada::tada:!")


@bot.hybrid_command()
async def ai(
    ctx: commands.Context,
    *,
    message: str = commands.param(
        description="The message to send to the AI"
    ),
) -> None:
    """Talk to Gemini AI"""
    async with ctx.typing():
        response = await genai_model.generate_content_async(
            message
        )
        lines = response.text.splitlines()
        i = 0
        while True:
            if i >= len(lines):
                return
            chunk = lines[i]
            if not chunk:
                i += 1
            elif "```" in chunk:
                j = i + 1
                chunk = lines[j]
                while j < len(lines) and "```" not in chunk:
                    j += 1
                    chunk = lines[j]
                await ctx.send("\n".join(lines[i:j+1]))
                i = j + 1
            else:
                await ctx.send(chunk)
                i += 1


def main():
    """Main function"""
    bot.run(os.environ["DISCORDPY_API_KEY"])


if __name__ == "__main__":
    main()

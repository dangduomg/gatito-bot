"""gatito-bot 2.0"""


import os
import random
import asyncio
from collections import deque
from typing import Generator

import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])  # type: ignore

genai_model = genai.GenerativeModel()  # type: ignore

intents = discord.Intents.default()
intents.message_content = True


def chunk_to_line(
    response: genai.types.GenerateContentResponse  # type: ignore
) -> Generator[str, None, None]:
    """Used for chunked responses. Turns chunks into lines"""
    buffer = deque([""])
    for chunk in response:
        buffer += (buffer.pop() + chunk.text).split("\n")
        while len(buffer) > 1:
            yield buffer.popleft()
    yield buffer.popleft()


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
        f"Please enter {numbers} numbers from 1 to {range_}" +
        "(You have 30 seconds to respond):"
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
        response = genai_model.generate_content(message, stream=True)
        lines = chunk_to_line(response)
        mode = "normal"
        output = []
        for line in lines:
            match mode:
                case "normal":
                    if not line:
                        continue
                    if "```" in line:
                        mode = "code"
                        output.append(line)
                    else:
                        await ctx.send(line)
                case "code":
                    output.append(line)
                    if "```" in line:
                        mode = "normal"
                        await ctx.send('\n'.join(output))
                        del output[:]


def main():
    """Main function"""
    bot.run(os.environ["DISCORDPY_API_KEY"])


if __name__ == "__main__":
    main()

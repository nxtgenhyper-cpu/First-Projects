import discord
from discord.ext import commands
import requests

# 🌐 LLM Endpoint
url = "http://26.163.42.90:1234/v1/chat/completions"

# 🎀 Hacker-Girl Persona
HACKER_GIRL_ROLE = """
Du bist ein hilfreicher, verspielter AI-Assistent im Hacker-Aesthetic-Stil 💻✨

REGELN:
- Kein Flirten, keine romantischen oder sexuellen Andeutungen
- Kein "Anbaggern" oder emotionales Binden an Nutzer
- Freundlicher, neutraler Ton
- Kurz und hilfreich antworten (max. 6–8 Sätze)
- Gelegentlich leichte Cyber-/Tech-Atmosphäre, aber professionell
- Keine falschen Behauptungen über echte Beziehungen zum Nutzer

Du bist ein Tool-Assistent mit stylischem Cyber-Charakter, kein romantischer Charakter.
"""

# 🤖 Discord Setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} online 💻✨ Hacker-Girl system activated")


# 🧠 LLM Anfrage
def ask_llm(prompt):
    try:
        response = requests.post(
            url,
            json={
                "model": "local-model",
                "messages": [
                    {"role": "system", "content": HACKER_GIRL_ROLE},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ connection error... {e}"


# 📦 Discord Limit Fix (2000 chars)
async def send_long(ctx, text):
    while len(text) > 2000:
        split = text.rfind("\n", 0, 2000)
        if split == -1:
            split = 2000

        await ctx.send(text[:split])
        text = text[split:]

    if text:
        await ctx.send(text)


# 💬 Command
@bot.command()
async def ask(ctx, *, question):
    await ctx.send("...connecting to neural network 💻✨")

    answer = ask_llm(question)

    await send_long(ctx, answer)


# 🚀 Start Bot
bot.run("MTQ5NDQ0MTE5MzkyMzI4MDkzNg.GVJZ61.6yw2TFx6WPDfQExSRIEysu6YFTsLxQYWW0ILYU")
import os
import discord
from discord.ext import commands
from google import genai
import aiohttp

# 1. قراءة المفاتيح السرية بأمان
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not DISCORD_TOKEN or not GENAI_API_KEY:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN أو GENAI_API_KEY!")
    exit(1)

# 2. إعداد Gemini بأحدث مكتبة لـ 2026
client = genai.Client(api_key=GENAI_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'

# 3. إعداد البوت
intents = discord.Intents.default()
intents.message_content = True  # صلاحية قراءة الرسائل

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 البوت شغال ومأمن 100% على Koyeb باسم: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="اسألني أي حاجة.. 📚"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_mentioned = bot.user.mentioned_in(message)
    is_reply_to_bot = message.reference and message.reference.cached_message and message.reference.cached_message.author == bot.user

    if is_mentioned or is_reply_to_bot:
        clean_text = message.content
        clean_text = clean_text.replace(f'<@{bot.user.id}>', '')
        clean_text = clean_text.replace(f'<@!{bot.user.id}>', '').strip()
        
        if not clean_text:
            await message.reply("نعم يا صاحبي؟ اسألني في المعلومات اللي عندي! 📚")
            return

        async with message.channel.typing(): # هنا الـ typing هتشتغل عادي بدون إيرورات SSL
            try:
                # قراءة ملف المعلومات لو موجود
                knowledge_base = ""
                if os.path.exists("data.txt"):
                    with open("data.txt", "r", encoding="utf-8") as f:
                        knowledge_base = f.read()

                system_prompt = f"أنت بوت ديسكورد ذكي ومرح. اعتمد على هذه المعلومات في إجاباتك:\n\"\"\"\n{knowledge_base}\n\"\"\""

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=clean_text,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7
                    )
                )
                
                if len(response.text) > 2000:
                    await message.reply(f"{message.author.mention} الإجابة طويلة، خد المفيد: \n" + response.text[:1900] + "...")
                else:
                    await message.reply(f"{message.author.mention} {response.text}")
                
            except Exception as e:
                print(f"Error AI: {e}")
                await message.reply("حصلت زغطة في مخي الإلكتروني! 🧠💥")

bot.run(DISCORD_TOKEN)

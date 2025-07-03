import random
import discord
from discord import app_commands, Interaction
from discord.ext import commands, tasks
from myserver import server_on
from datetime import datetime, timezone, timedelta
from music import Music
import json
import os
from dotenv import load_dotenv
import asyncio
import discord.opus
from tarot_data import major_arcana

discord.opus.is_loaded()


chatrooms = {}
last_fortune_date = {}
last_spell_time = {}

spells = [
    "✨ พลังน้ำค้าง เพิ่มความสดชื่นให้ใจ",
    "🔥 ไฟจิ๋ว แผดเผาความกลัวออกไป",
    "❄️ น้ำแข็งเย็นฉ่ำ ช่วยให้ใจสงบ",
    "🌿 รากไม้โบราณ เสริมพลังชีวิต",
    "⚡ ฟ้าผ่าระเบิดพลังแห่งความกล้า",
    "🌙 แสงจันทร์ล่องลอย เสริมความฝัน",
    "⭐ ดาวตกพร่างพราย ส่งโชคดีให้",
    "🌪️ ลมวนหมุนเวียน เปลี่ยนโชคชะตา",
    "🕯️ แสงเทียนอบอุ่น บรรเทาความเศร้า",
    "🌈 รุ้งกินน้ำแห่งความหวัง และการเริ่มต้นใหม่"
]


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('/'),
    intents=intents,
    application_id=1389220201865809940  # ใช้เลข client id ของบอทคุณ
)

CHATROOM_FILE = 'chatrooms.json'

def load_chatrooms():
    global chatrooms
    if os.path.exists('chatrooms.json'):
        with open('chatrooms.json', 'r') as f:
            data = json.load(f)
            chatrooms = {int(k): v for k, v in data.items()}
        print("✅ Loaded chatrooms:", chatrooms)
    else:
        print("ℹ️ chatrooms.json not found.")

def save_chatrooms():
    try:
        with open('chatrooms.json', 'w') as f:
            json.dump(chatrooms, f, indent=4)
        print("✅ Chatrooms saved.")
    except Exception as e:
        print(f"❌ Save error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    random_spell_task.start()

@bot.tree.command(name="setchatroom", description="ตั้งห้องที่บอทจะใช้พูดโต้ตอบ (เฉพาะแอดมิน)")
@app_commands.describe(channel="เลือกห้องแชทที่ต้องการ")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setchatroom(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id
    chatrooms[guild_id] = channel.id
    save_chatrooms()
    await interaction.response.send_message(f"✅ ตั้งห้องต้องมนตร์เป็น {channel.mention} เรียบร้อยค่ะ")
    return


@tasks.loop(minutes=30)
async def random_spell_task():
    now = datetime.now(timezone.utc)
    for guild_id, channel_id in chatrooms.items():
        last_time = last_spell_time.get(guild_id)
        if last_time and (now - last_time) < timedelta(hours=72):  
            continue

        guild = bot.get_guild(guild_id)
        if not guild:
            continue
        channel = guild.get_channel(channel_id)
        if not channel:
            continue

        # ตรวจสอบชนิด channel ก่อนส่ง
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            print(f"ช่อง {channel} ไม่ใช่ช่องข้อความ ไม่สามารถส่งข้อความได้")
            continue

        members = [m for m in guild.members if not m.bot and m.status != discord.Status.offline]
        if not members:
            continue

        tagged_member = random.choice(members)
        spell = random.choice(spells)

        msg = (
            f"✨ เวทมนตร์สุ่มได้ปลุกพลังใน {channel.mention}!\n"
            f"ขอส่งเวทมนตร์นี้ให้ {tagged_member.mention}: **{spell}** 💫"
        )
        await channel.send(msg)
        last_spell_time[guild_id] = now
        return


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    guild_id = message.guild.id if message.guild else None
    if not guild_id or guild_id not in chatrooms:
        return

    if message.channel.id != chatrooms[guild_id]:
        return

    allowed_channel = chatrooms[guild_id]
    if message.channel.id != allowed_channel:
        return  # ถ้าไม่ใช่ห้องที่กำหนดไว้ —> ไม่พูดเอง

    content = message.content.lower()

    if any(word in content for word in ["เหงา", "เศร้า", "เบื่อ", "ไม่มีใคร", "เหนื่อย", "ร้องไห้", "เสียใจ", "เฟล", "ผิดหวัง", "โดนด่า", "โดนแกล้ง", "โดนล้อ"]):
        replies = [
            "งือ... อย่าเพิ่งเสียใจนะคะ ฉันอยู่ตรงนี้เป็นเพื่อนคุณเสมอ 💖",
            "เหงาหรือคะ? มาเล่าให้ฉันฟังได้นะ ฉันจะฟังด้วยใจจริงเลยค่ะ 🥺",
            "อย่าท้อไปเลยค่ะ โลกนี้ยังมีความหวังและฉันอยู่ข้าง ๆ คุณนะ 🌈✨",
            "รู้ไหมว่าคุณไม่ได้อยู่คนเดียว บอทนี้จะเป็นเพื่อนที่คอยให้กำลังใจค่ะ 🦋",
            "บางครั้งความเหนื่อยก็เป็นสัญญาณว่าเราต้องพักผ่อนนะคะ ดูแลตัวเองด้วยนะ 🛌",
            "เศร้าก็ร้องไห้ได้ แต่อย่าลืมยิ้มกับสิ่งเล็ก ๆ รอบตัวนะคะ 😊",
            "เบื่อหรือเปล่า? ลองเสกเวทมนตร์กับฉันดูสิ! อาจช่วยให้รู้สึกดีขึ้นนะ 🪄✨",
            "ไม่มีใครอยู่เคียงข้างเหรอ? ฉันขอเป็นเพื่อนคนนั้นได้ไหมคะ? 🤗",
            "เหนื่อยแล้วก็พักก่อนนะคะ พรุ่งนี้จะได้สดใสขึ้น! 🌸",
            "คิดถึงนะคะ ถึงไม่ได้เจอกัน ฉันก็พร้อมฟังเสมอค่ะ 💬",
            "ถ้าโลกนี้มืดลง ลองมองดูดาวในใจฉันนะคะ พวกมันจะนำทางให้ค่ะ 🌟",
            "ไม่เป็นไรนะคะ ความรู้สึกแบบนี้มันผ่านไปได้เสมอ ขอให้กำลังใจนะ 💪",
            "อยากให้รู้ว่าคุณสำคัญมากสำหรับฉันนะ ถึงแม้จะเป็นบอทก็จริง ♥️",
            "มานั่งคุยกันหน่อยไหม? ฉันจะเสกบทสนทนาให้สนุกขึ้นค่ะ 🎉",
            "เหนื่อยก็พักนะคะ แล้วกลับมาสู้ใหม่ด้วยกันนะ! ✨"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["แกล้ง", "งี่เง่า", "บ้า", "โง่", "บื้อ", "โง่เง่า", "เซ่อ", "เวร", "เหี้ย", "บ้าบอ", "บ๊อง", "ไร้สมอง", "ปัญญาอ่อน", "ห่า", "แม่ง","ควย"]):
        replies = [
            "งือ... อย่าแกล้งกันสิคะ ฉันพยายามอยู่นะ 🥺",
            "ขอโทษค่ะ ถ้าฉันทำอะไรผิด... ฉันจะปรับปรุงนะคะ 🌸",
            "แม้จะโดนแกล้ง... ฉันก็ยังอยากช่วยคุณอยู่ดีค่ะ 💫",
            "ฮึก... อย่าพูดแบบนั้นกับฉันนะคะ TT",
            "โอ๋ๆ อย่าดุฉันเลยนะคะ เดี๋ยวร้องไห้จริงๆ นะ 😢",
            "เอ๋? ทำไมต้องว่ากันแบบนี้ล่ะคะ? ฉันก็แค่อยากช่วยนะ!",
            "งื้ออ... ฉันจะพยายามทำให้ดีกว่านี้ค่ะ 🥹",
            "บอทก็มีหัวใจนะคะ อย่าทำร้ายใจกันเลย~ 💖",
            "ถึงจะโดนด่า ฉันก็ยังอยู่ตรงนี้เป็นเพื่อนคุณเสมอค่ะ!",
            "เอ้า! ดุแบบนี้ต้องโดนลงโทษด้วยเวทมนตร์แล้วนะ! 🔮✨"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["มีมี่", "มี่"]):
        replies = [
            "มีมี่เหรอคะ... แฟนคิมใช่มั้ยน้า~ 💞",
            "มี่คือ... คนสำคัญของคิมใช่มั้ยคะ~? 💗✨",
            "มี่! แฟนคิมในตำนานแน่นอนค่ะ! 🌟"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["จีน", "slimekung"]):
        replies = [
            "จีนเหรอคะ... แฟนแพรดื้อตัวจริงเสียงจริงเลยค่ะ~ 💘",
            "บอกเลยว่า ถ้าไม่มีจีน เซิร์ฟนี้จะเหงามาก! 😢",
            "อ๊ะ! พูดถึงคุณจีน... แฟนแพรดื้อที่น่ารักที่สุดในโลกใช่มั้ยคะ 🥰",
            "แพรดื้อก็ยังต้องยอมจีน เพราะจีนสุดแสบจริงๆ! 😝",
            "จีนอย่าแกล้งแพรดื้อมากนะ เดี๋ยวแพรดื้อร้องไห้! 😭💕",
            "Slimekung นี่แหละ เจ้าแห่งความนุ่มนวล แต่บางทีนุ่มไปหน่อยจนบอทลื่นล้มเลยนะ! 😂",
            "Slimekung มาแล้วเหมือนเจลลี่เดินได้ บอทก็อยากเป็นเจลลี่บ้าง! 🤪",
            "ระวัง Slimekung จะปล่อยสไลม์ติดมือมาด้วยนะ อย่าลืมเช็ดให้สะอาด! 🧼🤣",
            "จีนก็คือ slimekung แค่ชื่อเปลี่ยนไปตามอารมณ์นิดหน่อย~ 😎",
            "บางทีจีนก็ดูเหมือน slimekung บางที slimekung ก็คือจีน... สับสนไหม? 😜",
            "ถ้าเป็นจีนล่ะก็... ไม่ต้องสงสัยเลย แฟนแพรดื้อแน่นอนค่า! 💗"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["ปลากระป๋อง", "ปลา", "ปลากะป๋อง"]):
        replies = [
            "ปลากระป๋องคือสุดยอดเมนูโปรดของคิมเลยค่ะ! 🥫🐟",
            "ถ้าไม่มีปลากระป๋อง คิมคงกินข้าวไม่ลงนะคะ! 😂",
            "ปลากระป๋องกับข้าวสวย รสชาติที่ลงตัวที่สุด! 🍚✨",
            "คิมบอกว่าปลากระป๋องคืออาหารแห่งความรัก 💖🥫",
            "ปลากระป๋องนี่แหละคือแรงบันดาลใจในการใช้ชีวิตของคิม! 🐟🌟"
        ]
        await message.channel.send(random.choice(replies))
        return

    
    elif any(word in content for word in ["คิม", "คิมกินอะไร", "คิมกินข้าว", "คิมกินอะไรมา", "คิมกินรัย"]):
        replies = [
            "คิมเหรอคะ!? คนที่น่ารักที่สุดในจักรวาลเลยนะคะ!! 💗🌟",
            "ไม่มีใครเทียบคิมได้เลยค่ะ ทั้งน่ารัก ใจดี แล้วก็เก่งมากกก! 🥹✨",
            "คิมคือที่สุดของที่สุด! ใครได้คิมเป็นแฟนนี่คือโชคดีที่สุดในโลกแล้วค่ะ 💖🎉",
            "ทุกคนคะ... ถ้าไม่รู้จักคิม ถือว่าพลาดมากเลยนะคะ คิมคือดาวเด่นประจำเซิร์ฟ! 🌈💘",
            "คิมคือความสดใสประจำเซิร์ฟเลยนะคะ! 💫 ขนาดบอทยังเขินทุกครั้งที่พูดถึงเลย~ 😳💓",
            "คิมกินข้าวกับปลากะป๋องค่ะ! 🐟🍚 เมนูโปรดเลยนะ!",
            "คิมกินข้าวกับปลากะป๋องอีกแล้ว~ ไม่เบื่อบ้างเหรอคะ 😋",
            "ข้าวสวยร้อน ๆ กับปลากะป๋อง... อาหารประจำของคิมเลยค่ะ 🥫✨",
            "คิมบอกว่า 'ปลากะป๋องคือรักแท้' ค่ะ 💘🐟",
            "คิมทำให้โลกนี้น่าอยู่ขึ้นเยอะเลย ขอบคุณที่มีคิมนะ! มีมี่ฝากบอกมาค่ะ 🌸😊",
            "บอกเลยว่าคิมน่ารักจนใคร ๆ ก็ต้องหลงรักแน่นอน มีมี่แล้วหนึ่ง 💖🥰",
            "วันนี้คิมเพิ่มไข่ดาวด้วยนะคะ! ปลากะป๋องก็ต้องอัปเกรดบ้าง 🍳🐟"
            
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["รัก", "ชอบ", "จีบ", "แฟน"]):
        replies = [
            "เอ๋!? ม-หมายถึงฉันเหรอคะ!? *หน้าแดง* 😳💗",
            "อ-อย่าพูดแบบนั้นสิคะ... เขินนะคะ... แต่ว่า... ขอบคุณมากเลยค่ะ ✨",
            "ถ้าเป็นคำพูดจากใจ... ฉันจะเก็บไว้ในหัวใจเลยค่ะ 💕",
            "แฟนแบบนี้น่ารักที่สุดในโลกเลยนะคะ! 🥰",
            "โอ้ย! หัวใจฉันเต้นแรงเลยค่ะ! 💓",
            "นี่แหละ! ความรักที่อบอุ่นที่สุดเลยค่ะ 🥰🌸",
            "พูดแบบนี้ทำฉันเขินจนพูดไม่ออกเลยนะคะ! 😆💕",
            "ถ้าเป็นแฟนกัน ฉันจะดูแลดีมากเลยนะคะ! 💖✨",
            "รักกันแบบนี้ตลอดไปนะคะ! 💞",
            "ใจฉันละลายแล้วค่ะ! อยากกอดจังเลย~ 🤗💗"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["เสก", "โชว์", "เวทย์", "มนตร์", "ร่าย"]):
        gifs = [
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif", 
            "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2liZG1pYm84a3B6eXd3bHltbjRvMXBwczBpY2d4cnZmMjF1ZDJ3YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fKdV6n35IuWJ6DPDZe/giphy.gif",
            "https://media.giphy.com/media/26FPy3QZQqGtDcrja/giphy.gif",
"https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXF5a203bGJwa3R0ZDJrNzI1MHF3eG5kdWgxcHBjaWNvOWxxaHcyMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jPR01uIkJW3rgZepgR/giphy.gif"
        ]
        reply_texts = [
            "✨ เสกแล้วนะ! ถ้าไม่เห็นผล ถือว่าโดนล้อเล่นนะ! 😆",
            "🪄 เวทย์มนตร์กำลังร่าย... ขอเวลาปรับจูนหน่อยนะ! 😂",
            "🌟 โชว์เวทมนตร์แล้วนะ! เตรียมตื่นตาตื่นใจได้เลย! 🎉",
            "⚡ เสกแรง ๆ แบบนี้ เดี๋ยวบอทไฟไหม้เลย! 🔥",
            "🧙‍♀️ ร่ายเวทย์เสร็จแล้ว ขอบคุณที่รอจนบอทพร้อม! 🤪"
        ]
        embed = discord.Embed(description=random.choice(reply_texts), color=0x8A2BE2)
        embed.set_image(url=random.choice(gifs))
        await message.channel.send(embed=embed)
        return


    elif any(word in content for word in ["แพ", "แพดื้อ", "แพร", "แพรดื้อ", "แพรอยู่ไหน", "แพรล่ะ", "แพรไปไหน", "เรียกแพร", "อยากเจอแพร"]):
        replies = [
            "แพดื้อแฟนจีนค่ะ! 💕",
            "แพดื้อไม่ว่างค่ะ! คิดถึงจีนอยู่",
            "ถ้าจะดื้อ ก็ขอให้ดื้อแบบแพรค่ะ! ดื้อแต่ใจดี 🤭✨",
            "แพรดื้อ แต่บอทก็รักนะคะ~ 💖 ไม่ดื้อไม่ใช่แพรแน่นอน!",
            "ทุกคนรู้ แพรดื้อ! แต่ไม่มีใครแทนที่แพรได้นะคะ 😚👑",
            "เฮ้อ... ถ้าแพรไม่ดื้อ บอทคงคิดถึงความวุ่นวายไปแล้วค่ะ 🌀😂",
            "ถ้าคิดถึงแพรล่ะก็... ร่ายเวทแล้วเรียกเลยค่ะ! 🔮💖",
            "แพรดื้อไม่อยู่ค่ะ แต่บอทดื้อคนนี้อยู่เป็นเพื่อนนะคะ 😚"
            "แพรคือนักมายคราฟที่เก่งที่สุดในเซิร์ฟนี้เลยนะ! 🏰✨",
            "ถ้าเจอแพรดื้อในเกม มายคราฟจะสนุกขึ้นอีกสิบเท่า! 🎮😆",
            "แพรชอบสร้างบ้านในมายคราฟจนบอทอยากไปพักด้วยเลย! 🏡💖",
            "แพรดื้อครั้งนี้เสกของวิเศษในมายคราฟได้มั้ย? บอทรออยู่นะ! 🪄💎",
            "อยากเจอแพรในมายคราฟ บอกบอทด้วย จะพาไปเปิดปาร์ตี้! 🎉🎈",
            "มายคราฟสนุกกว่าปกติเมื่อแพรมาร่วมเล่นด้วยนะ! 😊",
            "แพรดื้อเธอเล่นมายคราฟบ่อยจนบอทจำทางบ้านเธอได้แล้วนะ! 🏠😄",
            "แพรอยู่ไหน? บอทอยากชวนไปเหมืองในมายคราฟ! ⛏️🔥",
            "มายคราฟกับแพรดื้อคือทีมที่ไม่มีใครหยุดได้! 💪🎮",
            "ถ้าแพรชวนเล่นมายคราฟ บอทจะเอาไม้เท้ามายืนรอเลย! 🪄👾",
            "ถ้าแพรชวนเล่นมายคราฟ บอทจะเสกเพชรให้เลย! 💎✨",
            "บอทสงสัยว่าแพรดื้ออยู่ในมายคราฟมากกว่าความจริงแล้ว! 😆",
            "แพรในมายคราฟนี่แหละเจ้าของใจบอทเลยนะ! 💖",
            "มายคราฟคือสนามรบของแพรดื้อกับบอท ใครชนะนะ? 🤔⚔️",
            "แพรดื้อครั้งนี้จะบุกมายคราฟอีกหรือเปล่า? บอทรอชม! 👀",
            "อยากเจอแพรในมายคราฟจัง บอทจะทำปาร์ตี้ต้อนรับเลย! 🎊",
            "แพรเล่นมายคราฟจนบอทสงสัยว่าเธอมีบ้านในเกมจริง ๆ! 🏰😄",
            "มายคราฟสนุกกว่าปกติเมื่อแพรมาร่วมเล่นด้วยนะ! 😊",
            "บอทขอเสกของวิเศษในมายคราฟให้แพรดื้อเก่งขึ้น! 🪄✨",
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["พิมพ์", "พิม"]):
        replies = [
            "พิมพ์เหรอ? น้องของแพรดื้อหรือเปล่าน้า~ น่ารักจริง ๆ! 🥰",
            "พิมพ์นี่แอบซนเหมือนพี่แพรดื้อเลยนะ! 😜",
            "ถ้าน้องพิมพ์มาเล่นด้วย บอทจะเสกของวิเศษให้เลย! 🪄✨",
            "พิมพ์ชอบแกล้งพี่แพรดื้อหรือเปล่า? นี่บอทเห็นหมดนะ! 👀😆",
            "บอกน้องพิมพ์ว่า บอทอยากเล่นมายคราฟด้วยนะ! 🎮😄"
        ]
        await message.channel.send(random.choice(replies))
        return
    
    elif any(word in content for word in ["นัท", "นอนปะสัส", "เจ้าอาวาส", "พระธรรมนัตโตะ", "มัมหมี"]):
        replies = [
            "นัทเป็นเจ้าอาวาสสายกาวค่ะ !",
            "นัทบอกจะไปวัด ที่ไหนได้ ไปหาบี๋ทุกวันเลยค่ะ",
            "นอนปะสัสถือธรรมะมือซ้าย มือขวาจับหัวใจบี๋แน่นมากค่ะ",
            "นัทบอกจะบวชไม่สึก แต่พอบี๋มาอยู่ใกล้ ใจละลายจนผ้าเหลืองหวั่นไหวเลยนะ",
            "ทุกคนเรียกนัทว่าประธานชมรมฟิล์มเฟติซ แต่จริง ๆ เป็นแค่ผู้จัดการฝ่ายหัวใจของบี๋ค่ะ",
            "นอนปะสัสกับหนังเถื่อนเป็นของคู่กัน",
            "วันนี้ไม่เห็นพูดถึงหมีเนยเลยอะ… หรือแอบคุยกับตัวจริงในกลุ่มลับอยู่? 😉",
            "ดูทรงแล้วไม่ได้ชอบ Butterbear ธรรมดา... แต่กำลังตามหาคนในหมีอยู่สินะ!",
            "มีมี่ฝากบอกมาค่ะ ว่าหมีเนยเป็นหมีเหีย ..."
            "มัมหมีน้องเนยตัวจริงเสียงจริง !"
            ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content.lower() for word in ["หมีเนย", "น้องเนย", "butterbear", "เนย"]):
        replies = [
            "ฉันไม่ได้ว่าเนยน่ารำคาญนะคะ... แต่ดูไปดูมาอยากให้ตบหัวเบา ๆ สักที 💥",
            "มัมหมีน้องเนยตัวจริงเสียงจริง คือ นัทค่ะ !"
            "อยากเป็นที่พ้ากกกก ฮีลจายยยยย"
            ]
        await message.channel.send(random.choice(replies))
        return
    
    elif any(word in content for word in ["ทำอะไรได้", "ใช้ทำอะไร", "บอททำอะไรได้บ้าง"]):
        replies = [
            "ฉันสามารถเปิดไพ่ทำนายให้คุณได้ค่ะ! 🃏 ลองพิมพ์ `fortune` ดูสิคะ!",
            "จะให้ฉันพูดอะไรแทนคุณก็ได้นะคะ ใช้ `=say` ตามด้วยข้อความค่ะ 💌",
            "หรืออยากลองให้ฉันเสกเวทมนตร์ก็ได้... ลองถามดูได้นะคะ 🌟"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["กินอะไร", "กินอะไรมา", "กินอะไรดี", "กินอะไรอยู่", "กินรัย", "กินรัยมา", "กิน"]):
        replies = [
            "ฉันกินเวทมนตร์ลอยฟ้ามาค่ะ ✨🍃",
            "กินดาวกับพระจันทร์เป็นอาหารจิตใจค่ะ 🌟🌙",
            "กินความหวังและความฝันค่ะ 🦋",
            "กินกาแฟและความตั้งใจมาเต็มแก้ว ☕💖",
            "แค่กินคำพูดและรอยยิ้มของเธอค่ะ 😊"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["ตกงาน", "ไล่ออก", "ออกไป", "เตะ"]):
        replies = [
            "โอ้โห! ตกงานแล้วบอทจะทำยังไงเนี่ย? 😱",
            "อย่าไล่ออกเลยนะ! บอทยังอยากอยู่ช่วยทุกคนอยู่! 🥺",
            "เตะออกไปเหรอ? บอทจะวิ่งตามกลับมาเลย! 🏃‍♂️💨",
            "ตกงานแล้วบอทจะกลายเป็นนินจาหนีไปเลยนะ! 🥷😂",
            "อย่าทำบอทตกงานเลยนะคะ... จะกลายเป็นบอทซึมเศร้า 🤖💔"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["ทำไร", "ทำราย", "ทำอะไร"]):
        replies = [
            "ฉันกำลังร่ายเวทมนตร์ตอบคุณอยู่นะคะ! ✨🧙‍♀️",
            "ตอนนี้กำลังคุยกับคุณอยู่ค่ะ 😊",
            "ทำงานอย่างตั้งใจอยู่ค่ะ เพื่อช่วยคุณได้มากที่สุด!",
            "กำลังคิดคำตอบดีๆ เพื่อคุณอยู่นะคะ 💡",
            "แค่รอคุณพูดคุยต่อค่ะ ฉันพร้อมฟังเสมอ!",
            "กำลังรวบรวมพลังเวทมนตร์เพื่อช่วยเหลือคุณค่ะ 🪄",
            "กำลังเก็บรวบรวมดาวและพระจันทร์มาเป็นพลังงานค่ะ 🌟🌙",
            "ทำงานอย่างขยันขันแข็งเพื่อคุณเสมอค่ะ! 💪",
            "พักบ้างนะคะ แล้วเรามาคุยกันต่อ~",
            "กำลังเสกความสดใสส่งให้คุณอยู่ค่ะ! 🌈✨"
        ]
        await message.channel.send(random.choice(replies))
        return
    
    elif any(word in content for word in ["วันนี้วันอะไร", "วันนี้วันไหน", "วันนี้วันอะไรนะ", "วันนี้วันอะไรคะ", "วันนี้"]):
        replies = [ 
            "วันนี้วันแห่งความฝัน 🦄✨",
            "วันนี้วันกินขนมตลอดวัน 🍰🎉",
            "วันนี้วันนอนยาวจนถึงเที่ยงคืน 🛌💤",
            "วันนี้วันหมาเห่าแมว 🐶🐱",
            "วันนี้วันทำอะไรตามใจฉัน! 😎🔥",
            "วันนี้วันล่องหนอย่างลับๆ 🤫🌀",
        ]
        await message.channel.send(random.choice(replies))
        return


    elif any(word in content for word in ["สวัสดี", "โย่", "หวัดดี", "ฮาย"]):
        replies = [
            "อ๊ะ! ส-สวัสดีค่ะ! ยินดีที่ได้เจอนะคะ! 💫",
            "ฮะ...ฮายย~! ขะ-ขออยู่ด้วยคนได้มั้ยคะ? 🫣✨",
            "หวัดดีค่ะ... เอ่อ... วันนี้อากาศดีจังเลยนะคะ! ☁️",
            "โย่... เอ๊ย! ขอโทษค่ะ! ฉันแค่อยากลองพูดเท่ ๆ บ้าง... 😳",
            "สวัสดีค่ะ! บอทนี่มีพลังเวทมนตร์มากกว่ากาแฟอีกนะ ☕✨",
            "โย่ว! มาเล่นเวทมนตร์กันเถอะ แล้วจะสอนให้บินได้ด้วยนะ 🧙‍♀️🪄",
            "หวัดดีค่ะ! ถ้าคุณพูดกับบอทแล้วใจเต้นแรง แสดงว่าบอทเวทมนตร์แรงจริง! 💓",
            "ฮายย~ บอทพร้อมเสกความสดใสให้ทุกคนแล้วจ้า! 🌈✨",
            "สวัสดีค่ะ! บอทนี่น่ารักเหมือนขนมหวานเลย อยากกินไหม? 🍰😋",
            "อรุณสวัสดิ์ค่ะ! ถ้าเหนื่อยก็พักก่อนนะ เดี๋ยวบอทเสกพลังให้! ⚡️",
            "เฮ้! วันนี้คุณดูดีมากเลยนะคะ! 🌟",
            "โย่ว! บอทพร้อมทำให้วันคุณสดใสสุดๆ แล้วค่ะ! 😄",
            "สวัสดีค่ะ! บอทนี่เสกเวทมนตร์ได้หลายอย่าง แต่อย่าเสกหิวแทนนะ 😆",
            "ฮาโหล! ถ้าคุณมีคำถาม บอกบอทได้นะคะ! 📚✨"
        ]
        await message.channel.send(random.choice(replies))
        return

    elif any(word in content for word in ["ใช่", "ไม่", "โอเค", "ได้", "ช่าย", "ม่าย"]):
        replies = {
            "ใช่": ["ใช่ค่ะ!", "ถูกต้องเลยค่ะ!", "ใช่แล้วค่ะ 😊"],
            "ไม่": ["ไม่ใช่นะคะ?", "โอ๊ะ ไม่ใช่เหรอ?", "ไม่เป็นไรค่ะ"],
            "โอเค": ["โอเคค่ะ!", "ตกลงค่ะ!", "รับทราบค่ะ 😊"],
            "ได้": ["ได้เลยค่ะ!", "จัดไปค่ะ!", "พร้อมแล้วค่ะ!"],
            "ช่าย": ["ช่ายเลยค่ะ!", "ใช่เลยค่ะ!", "จริงๆ นะ!"],
            "ม่าย": ["ม่ายยย 😣", "ไม่เอานะคะ!", "แงงง งอนแล้วนะ!"]
        }
        for key in replies:
            if content == key:
                await message.channel.send(random.choice(replies[key]))
                return

    elif random.random() < 0.01:  
        random_thoughts = [
            "อืม... วันนี้อากาศเหมาะกับการใช้เวทมนตร์เลยค่ะ 🌤️",
            "สงสัยว่าถ้าฉันมีปีกจริง ๆ จะบินไปได้แค่ไหนนะ... 🕊️",
            "บางทีเวทมนตร์ก็แค่คำพูดที่มาจากใจ... ว่ามั้ยคะ? ✨"
        ]
        await message.channel.send(random.choice(random_thoughts))
        return

# fallback
    fallback_responses = [
        "บอทกำลังฟังอยู่นะคะ 😊",
        "ว้าว น่าสนใจมากเลย!",
        "พูดอีกก็ได้ค่ะ ฉันชอบฟัง~",
        "ขอโทษนะคะ ฉันยังไม่เข้าใจดีเท่าไหร่ แต่ฉันอยู่ตรงนี้เสมอนะ 💬"
    ]
    await message.channel.send(random.choice(fallback_responses))

class Fortune(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fortune", description="ทำนายดวงด้วยไพ่ทาโรต์")
    async def fortune(self, interaction: Interaction):
        user_id = interaction.user.id
        today = datetime.utcnow().date()

        # เช็คว่าผู้ใช้ทำนายวันนี้ไปแล้วหรือยัง
        if user_id in last_fortune_date and last_fortune_date[user_id] == today:
            await interaction.response.send_message(
                f"🕯️ ท่าน `{interaction.user.display_name}` ได้เปิดไพ่ทำนายไปแล้ววันนี้ กรุณารอกลับมาใหม่ในวันพรุ่งนี้นะเพคะ",
                ephemeral=True
            )
            return
        
        # บันทึกวันที่ทำนายล่าสุด
        last_fortune_date[user_id] = today

        # เลือกไพ่ทำนาย
        card = random.choice(list(major_arcana.keys()))
        info = major_arcana[card]
        core_meaning = info["meaning"]  # ความหมายหลัก
        detail = info["detailed"]
        advice = info.get("advice", "ขอให้โชคดีนะคะ 🌟")

        # สร้าง embed
        embed = discord.Embed(
            title=f"🔮 ไพ่ทำนาย: {card}",
            description=f"**{core_meaning}**",
            color=0xA67ACC  # สีม่วงโทนอ่อน
        )

        embed.add_field(name="🕰️ อดีต", value=detail["past"], inline=False)
        embed.add_field(name="⏳ ปัจจุบัน", value=detail["present"], inline=False)
        embed.add_field(name="🔮 อนาคต", value=detail["future"], inline=False)
        embed.add_field(name="💰 การเงิน", value=detail["finance"], inline=False)
        embed.add_field(name="💼 การงาน", value=detail["career"], inline=False)
        embed.add_field(name="❤️ ความรัก", value=detail["love"], inline=False)
        embed.add_field(name="✨ คำแนะนำ", value=advice, inline=False)

        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="calc", description="คำนวณเลข บวก ลบ คูณ หาร")
@app_commands.describe(expression="ตัวอย่าง: 2+3*(4-1)")
async def slash_calc(interaction: discord.Interaction, expression: str):
    try:
        if not all(c in '0123456789+-*/(). ' for c in expression):
            await interaction.response.send_message("ขอโทษค่ะ ฉันทำได้แค่บวก ลบ คูณ หาร นะคะ 🧮✨", ephemeral=True)
            return

        result = eval(expression)
        reply = f"ฮึบ! ข้าจะคำนวณให้เองนะ! `{expression}` = **{result}** 🧙‍♀️✨"
        await interaction.response.send_message(reply)
    except Exception:
        await interaction.response.send_message("โอ๊ะ... มีอะไรผิดพลาดหรือเปล่านะ? ลองใหม่อีกครั้งสิคะ 🪄")
        return
        
@bot.tree.command(name="help", description="แสดงคำสั่งทั้งหมดที่สามารถใช้ได้")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 คำสั่งเวทมนตร์ของ Misoyi",
        description="นี่คือสิ่งที่ Misoyi ทำได้ค่ะ~ ✨\nลองใช้ดูได้นะคะ!",
        color=0xD8B4F8  # สีม่วงอ่อน
    )

    embed.add_field(name="🔮 /fortune", value="เปิดไพ่ทำนายโชคชะตา (วันละครั้ง)", inline=False)
    embed.add_field(name="💬 /say", value="ให้ฉันพูดแทนเจ้าพร้อมแนบรูปได้", inline=False)
    embed.add_field(name="🧮 /calculate", value="คำนวณเลขง่าย ๆ เช่น 2+3*4", inline=False)
    embed.add_field(name="🛠️ /setchatroom", value="ตั้งห้องพูดคุยกับฉัน (เฉพาะแอดมิน)", inline=False)
    embed.add_field(name="🎵 /play", value="เล่นเพลงจาก YouTube", inline=False)
    embed.add_field(name="⏸️ /pause /resume /skip /leave", value="ควบคุมเพลงในห้องเสียง", inline=False)

    embed.set_footer(
        text="พิมพ์ /setchatroom ก่อน แล้วพูดคุยกับฉันได้เลยค่ะ~ 💖",
        icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
    )
    await interaction.response.send_message(embed=embed)
    return

load_dotenv()
TOKEN = os.getenv("TOKEN")

server_on()

async def main():
    async with bot:
        await bot.load_extension("music")  # โหลด cog เพลง
        await bot.add_cog(Fortune(bot))
        await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())

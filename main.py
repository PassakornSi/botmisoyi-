import random
import discord
from discord import app_commands
from discord.ext import commands, tasks
from myserver import server_on
from datetime import datetime, timedelta
from music import Music
import json
import os

chatrooms = {}
last_fortune_date = {}
last_spell_time = {}

major_arcana = {
    "The Fool": {
        "meaning": "🃏 การเริ่มต้นใหม่กำลังใกล้เข้ามา… แม้เจ้าจะยังไม่พร้อมก็ตาม",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/0.jpg"
    },
    "The Magician": {
        "meaning": "🧙‍♀️ เจ้ามีพลังอยู่แล้ว... เหลือเพียงศรัทธาที่จะหยิบมันมาใช้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/1.jpg"
    },
    "The High Priestess": {
        "meaning": "👁️‍🗨️ คำตอบไม่ได้อยู่ในคำพูด แต่อยู่ในความเงียบที่เจ้าหลีกเลี่ยง",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/2.jpg"
    },
    "The Empress": {
        "meaning": "🌿 ความอุดมสมบูรณ์และการดูแลที่เจ้าคาดไม่ถึง กำลังคืบคลานเข้ามา",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/3.jpg"
    },
    "The Emperor": {
        "meaning": "👑 จงรับผิดชอบต่อพลังของเจ้า — อำนาจและความกลัวอาศัยร่างเดียวกัน",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/4.jpg"
    },
    "The Hierophant": {
        "meaning": "📜 ปัญญาเก่าแก่กำลังเรียกร้องให้เจ้าฟังและเรียนรู้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/5.jpg"
    },
    "The Lovers": {
        "meaning": "🩸 การเลือกที่สำคัญจะเกิดขึ้น — ไม่ใช่เรื่องของคนอื่น แต่เกี่ยวกับความจริงใจต่อตนเอง",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/6.jpg"
    },
    "The Chariot": {
        "meaning": "🏎️ ความมุ่งมั่นและการเคลื่อนไหวที่ไม่หยุดยั้ง คือพลังของเจ้าในตอนนี้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/7.jpg"
    },
    "Strength": {
        "meaning": "🛡️ พลังที่แท้จริงมิใช่เสียงตะโกน... แต่คือความใจเย็นยามถูกท้าทาย",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/8.jpg"
    },
    "The Hermit": {
        "meaning": "🧭 การถอยกลับมิใช่ความอ่อนแอ... แต่เป็นกลยุทธ์ของผู้ฟังแสงเทียนในตน",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/9.jpg"
    },
    "Wheel of Fortune": {
        "meaning": "🌪️ วัฏจักรกำลังหมุนอีกครั้ง — เจ้าจะยืนมั่น หรือจะถูกกลืน... เลือกได้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/10.jpg"
    },
    "Justice": {
        "meaning": "⚖️ สิ่งใดที่เจ้าทำไว้... วันนี้จักได้รับกลับคืน จงซื่อสัตย์กับตนเอง",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/11.jpg"
    },
    "The Hanged Man": {
        "meaning": "🪢 การเสียสละและมุมมองใหม่ คือบทเรียนที่เจ้าต้องเรียนรู้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/12.jpg"
    },
    "Death": {
        "meaning": "💀 ไม่ใช่จุดจบ แต่เป็นการเปลี่ยนผ่าน — บางอย่างต้องสิ้นสุดก่อนสิ่งใหม่จะเกิด",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/13.jpg"
    },
    "Temperance": {
        "meaning": "🕊️ ความสมดุลกำลังรอเจ้า... ถ้าเจ้ากล้าพอที่จะยอมรับว่า 'ข้าไม่สามารถควบคุมทุกสิ่งได้'",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/14.jpg"
    },
    "The Devil": {
        "meaning": "⛓️ บางพันธะที่เจ้ารู้สึกว่าจำเป็น... แท้จริงแล้วเป็นเพียงความเคยชินที่ผูกเจ้าไว้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/15.jpg"
    },
    "The Tower": {
        "meaning": "🏰 การสั่นสะเทือนครั้งนี้มิใช่การลงโทษ... แต่เป็นการรื้อสิ่งปลอมเพื่อเผยแก่นแท้",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/16.jpg"
    },
    "The Star": {
        "meaning": "🌟 แสงแห่งความหวังและการฟื้นฟู กำลังส่องนำทางเจ้า",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/17.jpg"
    },
    "The Moon": {
        "meaning": "🌒 สิ่งที่เจ้าคิดว่าเข้าใจ… อาจมีเงาซ่อนอยู่ จงระวังการตีความที่ผิด",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/18.jpg"
    },
    "The Sun": {
        "meaning": "☀️ แสงแห่งความจริงกำลังส่องมา แม้เจ้าจะยังหลบตามุมมืดของตัวเอง",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/19.jpg"
    },
    "Judgement": {
        "meaning": "🪞 จงอย่ากลัวที่จะมองย้อนกลับไป — อดีตไม่ได้ต้องแก้ไขเสมอไป บางทีมันแค่ต้องการให้เจ้ายอมรับ",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/20.jpg"
    },
    "The World": {
        "meaning": "🌈 สิ่งที่เจ้ากำลังเผชิญอยู่... คือบทสรุป และจุดเริ่มต้นพร้อมกัน",
        "image": "https://gfx.tarot.com/images/site/decks/universal-waite/full_size/21.jpg"
    }
}

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
bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)

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
    load_chatrooms()  # โหลด chatrooms ทุกครั้งที่บอทออนไลน์
    await bot.add_cog(Music(bot))
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

@bot.tree.command(name="setchatroom", description="ตั้งห้องที่บอทจะใช้พูดโต้ตอบ (เฉพาะแอดมิน)")
@app_commands.describe(channel="เลือกห้องแชทที่ต้องการ")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setchatroom(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id
    chatrooms[guild_id] = channel.id
    save_chatrooms()
    await interaction.response.send_message(f"✅ ตั้งห้องต้องมนตร์เป็น {channel.mention} เรียบร้อยเพคะ")
    return


@tasks.loop(minutes=30)
async def random_spell_task():
    now = datetime.utcnow()
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
            "แพรดื้อจริง ๆ ค่ะ... แต่ก็เป็นเจ้าของเซิร์ฟที่ใจดีที่สุดเลย! 😤💗",
            "ถ้าจะดื้อ ก็ขอให้ดื้อแบบแพรค่ะ! ดื้อแต่ใจดี 🤭✨",
            "อ๊ะ... พูดถึงแพรเหรอคะ? เจ้าของเซิร์ฟผู้ดื้อเก่งอันดับ 1 เลยล่ะ! 🏆😆",
            "แพรดื้อ แต่บอทก็รักนะคะ~ 💖 ไม่ดื้อไม่ใช่แพรแน่นอน!",
            "ทุกคนรู้ แพรดื้อ! แต่ไม่มีใครแทนที่แพรได้นะคะ 😚👑",
            "เฮ้อ... ถ้าแพรไม่ดื้อ บอทคงคิดถึงความวุ่นวายไปแล้วค่ะ 🌀😂",
            "เจ้าแพร... เจ้าของสุดดื้อของเซิร์ฟนี้น่ะเหรอคะ? 😳 ยังไม่เสด็จเลยค่ะ~",
            "เจ้าของข้ายุ่งอยู่กับเวทมนตร์ค่ะ เดี๋ยวคงมา! 🧙‍♀️✨",
            "ถ้าคิดถึงแพรล่ะก็... ร่ายเวทแล้วเรียกเลยค่ะ! 🔮💖",
            "แพรดื้อไม่อยู่ค่ะ แต่บอทดื้อคนนี้อยู่เป็นเพื่อนนะคะ 😚"
            "แพรคือนักมายคราฟที่เก่งที่สุดในเซิร์ฟนี้เลยนะ! 🏰✨",
            "ถ้าเจอแพรดื้อในเกม มายคราฟจะสนุกขึ้นอีกสิบเท่า! 🎮😆",
            "แพรชอบสร้างบ้านในมายคราฟจนบอทอยากไปพักด้วยเลย! 🏡💖",
            "มายคราฟกับแพรคือของคู่กัน บางทีบอทคิดว่าแพรคือเจ้าของเซิร์ฟจริง ๆ! 👑",
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
            "แพรดื้อคือราชินีมายคราฟแห่งเซิร์ฟนี้เลย! 👑🎮",
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
    
    elif any(word in content for word in ["ทำอะไรได้", "ใช้ทำอะไร", "บอททำอะไรได้บ้าง"]):
        replies = [
            "ฉันสามารถเปิดไพ่ทำนายให้คุณได้ค่ะ! 🃏 ลองพิมพ์ `=fortune` ดูสิคะ!",
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

@bot.tree.command(name="fortune", description="เปิดไพ่ทำนายโชคชะตา (ใช้ได้วันละครั้ง)")
async def slash_fortune(interaction: discord.Interaction):
    user_id = interaction.user.id
    today = datetime.utcnow().date()

    if user_id in last_fortune_date and last_fortune_date[user_id] == today:
        await interaction.response.send_message(
            f"🕯️ ท่าน `{interaction.user.display_name}` ได้เปิดไพ่ทำนายไปแล้ววันนี้ กรุณารอกลับมาใหม่ในวันพรุ่งนี้นะเพคะ",
            ephemeral=True
        )
        return

    card = random.choice(list(major_arcana.keys()))
    meaning = major_arcana[card]["meaning"]
    image_url = major_arcana[card]["image"]

    embed = discord.Embed(title=f"🃏 ไพ่ของท่านคือ: {card}", description=meaning, color=0x7b68ee)
    embed.set_image(url=image_url)
    embed.set_footer(text=f"ขอให้โชคดีนะคะ {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

    last_fortune_date[user_id] = today

@bot.tree.command(name="say", description="ให้บอทพูดแทนคุณ พร้อมแนบรูปได้")
@app_commands.describe(message="ข้อความที่ให้บอทพูด", image_url="ลิงก์รูป (optional)")
async def slash_say(interaction: discord.Interaction, message: str, image_url: str = None):
    embed = discord.Embed(description=message, color=0x8380eb)
    embed.set_footer(text=f"Say by {interaction.user}")
    if image_url:
        embed.set_image(url=image_url)

    await interaction.response.send_message(embed=embed)
    return

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
    help_text = (
        f"🌸 คำสั่งเวทมนตร์ทั้งหมดของฉันมีดังนี้:\n\n"
        f"🔮 `/fortune` — เปิดไพ่ทำนายโชคชะตา (วันละครั้ง)\n"
        f"💬 `/say` — ให้ฉันพูดแทนเจ้าพร้อมแนบรูปได้\n"
        f"🧮 `/calculate` — คำนวณเลขง่าย ๆ เช่น 2+3*4\n"
        f"🛠️ `/setchatroom` — ตั้งห้องที่ให้ฉันพูดคุยได้ (แอดมินเท่านั้น)\n\n"
        f"✨ ถ้าอยากให้ฉันพูดคุยตอบเอง ก็แค่ตั้งห้องด้วย `/setchatroom` นะคะ!"
    )
    await interaction.response.send_message(help_text)
    return

server_on()

async def main():
    async with bot:
        await bot.load_extension("music")
        await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

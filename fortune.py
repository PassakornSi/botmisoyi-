import random
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from tarot_data import major_arcana  # สมมติไฟล์ tarot_data.py เก็บข้อมูลไพ่

class Fortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_fortune_date = {}  # เก็บ user_id: date

    @app_commands.command(name="fortune", description="ทำนายดวงด้วยไพ่ทาโรต์")
    async def fortune(self, interaction: Interaction):
        user_id = interaction.user.id
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date()

        # เช็คว่าผู้ใช้เคยใช้คำสั่งวันนี้หรือยัง
        if user_id in self.last_fortune_date and self.last_fortune_date[user_id] == today:
            await interaction.response.send_message(
                f"🕯️ ท่าน `{interaction.user.display_name}` ได้เปิดไพ่ทำนายไปแล้ววันนี้ กรุณารอกลับมาใหม่ในวันพรุ่งนี้นะคะ",
                ephemeral=True
            )
            return

        card = random.choice(list(major_arcana.keys()))
        info = major_arcana[card]
        core_meaning = info["meaning"]  # ความหมายหลัก
        detail = info["detailed"]  # รายละเอียด
        advice = info.get("advice", "ขอให้โชคดีนะคะ 🌟")

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

        # บันทึกวันที่ใช้งาน
        self.last_fortune_date[user_id] = today

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fortune(bot))

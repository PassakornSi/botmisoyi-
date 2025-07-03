import random
import discord
from discord.ui import View, Button
from discord import Embed, Interaction, app_commands
from discord.ext import commands, tasks
from tarot_data import major_arcana  # สมมติไฟล์ tarot_data.py เก็บข้อมูลไพ่

class FortuneView(View):
    def __init__(self, card_data):
        super().__init__(timeout=None)  # ✅ ไม่มีวันหมดอายุ (อยู่ตลอดไปจนข้อความโดนลบ)
        self.card_data = card_data
        self.fields = ["past", "present", "future", "finance", "career", "love", "advice"]
        self.labels = {
            "past": "🕰️ อดีต",
            "present": "⏳ ปัจจุบัน",
            "future": "🔮 อนาคต",
            "finance": "💰 การเงิน",
            "career": "💼 การงาน",
            "love": "❤️ ความรัก",
            "advice": "✨ คำแนะนำ"
        }
        self.index = 0

    def create_embed(self):
        title = f"🔮 ไพ่ทำนาย: {self.card_data['name']}"
        color = 0xA67ACC
        image_url = self.card_data.get("image_url")

        embed = Embed(title=title, color=color)

        if self.index == 0:
            embed.description = f"💭 {self.card_data['meaning']}"
            if image_url:
                embed.set_image(url=image_url)  # หน้าแรกโชว์ภาพใหญ่
        else:
            key = self.fields[self.index - 1]
            label = self.labels[key]
            value = self.card_data['detailed'].get(key, self.card_data.get('advice', ''))
            embed.description = f"{label}\n{value}"
            if image_url:
                embed.set_thumbnail(url=image_url)  # หน้าอื่นโชว์ thumbnail

        embed.set_footer(text=f"หน้าที่ {self.index+1} / 8")
        return embed


    async def update_message(self, interaction: Interaction):
        embed = self.create_embed()
        if interaction.response.is_done():
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                view=self
            )
        else:
            await interaction.response.edit_message(
                embed=embed,
                view=self
            )

    @discord.ui.button(label="ก่อนหน้า", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: Interaction, button: Button):
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="ถัดไป", style=discord.ButtonStyle.primary)
    async def next(self, interaction: Interaction, button: Button):
        if self.index < len(self.fields):
            self.index += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        # ลองอัปเดตข้อความล่าสุด (view ต้องรู้ว่าอยู่ใน message ไหน)
        # ต้องแน่ใจว่า interaction.message ถูกอ้างถึงก่อนหน้านี้
        try:
            # สมมติว่า view ถูกแนบกับข้อความเดียวกันตอนส่ง
            message = self.message  # ต้องเซ็ต self.message เองตอนแรก
            await message.edit(view=self)
        except Exception as e:
            print(f"[on_timeout] ไม่สามารถปิดปุ่มได้: {e}")


class Fortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_fortune_date = {}  # เก็บ user_id: date

    @app_commands.command(name="fortune", description="ทำนายดวงด้วยไพ่ทาโรต์")
    async def fortune(self, interaction: Interaction):
        from datetime import datetime, timezone
        user_id = interaction.user.id
        today = datetime.now(timezone.utc).date()

        if user_id in self.last_fortune_date and self.last_fortune_date[user_id] == today:
            await interaction.response.send_message(
                f"🕯️ ท่าน `{interaction.user.display_name}` ได้เปิดไพ่ทำนายไปแล้ววันนี้ กรุณารอกลับมาใหม่ในวันพรุ่งนี้นะคะ",
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            card = random.choice(list(major_arcana.keys()))
            info = major_arcana[card]

            # เพิ่มชื่อไพ่ไว้ใน dict ด้วย เพื่อใช้ใน FortuneView
            info["name"] = card

            view = FortuneView(info)
            embed = view.create_embed()

            await interaction.followup.send(embed=embed, view=view)

            self.last_fortune_date[user_id] = today

        except Exception as e:
            print(f"Error in fortune command: {e}")
            await interaction.followup.send("❌ เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้งค่ะ")


async def setup(bot):
    await bot.add_cog(Fortune(bot))

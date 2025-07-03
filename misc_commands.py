# misc_commands.py
import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say", description="ให้บอทพูดแทนคุณ พร้อมแนบรูปได้")
    @app_commands.describe(message="ข้อความที่ให้บอทพูด", image_url="ลิงก์รูป (optional)")
    async def slash_say(self, interaction: Interaction, message: str, image_url: str = None):
        embed = discord.Embed(description=message, color=0x8380eb)
        embed.set_footer(text=f"Say by {interaction.user}")
        if image_url:
            embed.set_image(url=image_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calc", description="คำนวณเลข บวก ลบ คูณ หาร")
    @app_commands.describe(expression="ตัวอย่าง: 2+3*(4-1)")
    async def slash_calc(self, interaction: Interaction, expression: str):
        try:
            if not all(c in '0123456789+-*/(). ' for c in expression):
                await interaction.response.send_message("ขอโทษค่ะ ฉันทำได้แค่บวก ลบ คูณ หาร นะคะ 🧮✨", ephemeral=True)
                return

            result = eval(expression)
            reply = f"ฮึบ! ข้าจะคำนวณให้เองนะ! `{expression}` = **{result}** 🧙‍♀️✨"
            await interaction.response.send_message(reply)
        except Exception:
            await interaction.response.send_message("โอ๊ะ... มีอะไรผิดพลาดหรือเปล่านะ? ลองใหม่อีกครั้งสิคะ 🪄")

# จำเป็นต้องมีฟังก์ชัน setup เพื่อให้โหลด extension ได้
async def setup(bot):
    await bot.add_cog(Misc(bot))

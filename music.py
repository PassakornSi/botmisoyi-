import discord
from discord.ext import commands
from discord import app_commands, Interaction
import yt_dlp
import asyncio

class MusicControlView(discord.ui.View):
    def __init__(self, music_cog):
        super().__init__(timeout=None)
        self.music_cog = music_cog

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.pause(interaction)
        await interaction.response.send_message("⏸️ เพลงหยุดชั่วคราว", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.secondary)
    async def resume_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.resume(interaction)
        await interaction.response.send_message("▶️ เล่นเพลงต่อ", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.skip(interaction)
        await interaction.response.send_message("⏭️ ข้ามเพลง", ephemeral=True)

    @discord.ui.button(label="⏹️ Leave", style=discord.ButtonStyle.secondary)
    async def leave_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.leave(interaction)
        await interaction.response.send_message("⏹️ ออกจากช่องเสียงแล้ว", ephemeral=True)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_duration_str(self, seconds):
        # แปลงวินาทีเป็น mm:ss
        m, s = divmod(seconds, 60)
        return f"{int(m):02d}:{int(s):02d}"

    @app_commands.command(name="play", description="เล่นเพลงจาก URL หรือชื่อเพลง")
    @app_commands.describe(query="URL หรือชื่อเพลงที่ต้องการเล่น")
    async def play(self, interaction: Interaction, query: str):
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ คุณต้องอยู่ในช่องเสียงก่อนสั่งเล่นเพลงนะคะ!")
            return

        voice_channel = interaction.user.voice.channel
        guild = interaction.guild
        voice_client = guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        # ✅ ใส่ ytdlp_opts ที่นี่เลย
        ytdlp_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 10
        }

        try:
            ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)

            info = await asyncio.wait_for(
                self.bot.loop.run_in_executor(None, lambda: ytdlp.extract_info(query, download=False)),
                timeout=30
            )

            if 'entries' in info:
                info = info['entries'][0]
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ โหลดข้อมูลเพลงนานเกินไป กรุณาลองใหม่ค่ะ")
            return
        except Exception as e:
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {e}")
            return

        url = info['url']
        title = info.get('title', 'Unknown title')
        duration_sec = info.get('duration', 0)
        duration_str = self.get_duration_str(duration_sec)
        webpage_url = info.get('webpage_url', None)
        thumbnail = info.get('thumbnail', None)

        # สร้าง source สำหรับเล่นเสียง
        source = discord.FFmpegPCMAudio(
            url,
            executable=r"C:\Users\ASUS\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe",
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        )


        # เล่นเพลง
        if voice_client.is_playing():
            voice_client.stop()

        voice_client.play(source)

        # สร้าง Embed สวย ๆ
        embed = discord.Embed(
            title="🎵 กำลังเล่นเพลง",
            description=f"**{title}**\n\n⏳ ความยาว: `{duration_str}`",
            color=0xD8B4F8  # ม่วงอ่อน
        )

        if webpage_url:
            embed.url = webpage_url
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        embed.set_footer(text="โดย Misoyi Bot • 💜")


        # สร้าง view ปุ่ม
        view = MusicControlView(self)

        await interaction.followup.send(embed=embed, view=view)

    async def pause(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()

    async def resume(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()

    async def skip(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()

    async def leave(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))



import discord
from discord.ext import commands
from discord import app_commands, Interaction
import yt_dlp
import asyncio

async def setup(bot):
    await bot.add_cog(Music(bot))
    
class MusicControlView(discord.ui.View):
    def __init__(self, music_cog):
        super().__init__(timeout=None)
        self.music_cog = music_cog

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.pause(interaction)
        await interaction.response.send_message("⏸️ เพลงหยุดชั่วคราว", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.success)
    async def resume_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.resume(interaction)
        await interaction.response.send_message("▶️ เล่นเพลงต่อ", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.music_cog.skip(interaction)
        await interaction.response.send_message("⏭️ ข้ามเพลง", ephemeral=True)

    @discord.ui.button(label="⏹️ Leave", style=discord.ButtonStyle.danger)
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
        await interaction.response.defer()  # แจ้งว่ากำลังโหลด

        # เช็คว่าผู้ใช้อยู่ในช่องเสียงไหม
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ คุณต้องอยู่ในช่องเสียงก่อนสั่งเล่นเพลงนะคะ!")
            return

        voice_channel = interaction.user.voice.channel
        guild = interaction.guild

        # เช็คว่า bot อยู่ในช่องเสียงไหม ถ้าไม่อยู่ให้ join
        voice_client = guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        # ใช้ yt-dlp ดึงข้อมูลเพลง
        ytdlp_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'skip_download': True,
        }

        ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)
        info = None
        try:
            info = ytdlp.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
        except Exception as e:
            await interaction.followup.send(f"❌ หาเพลงไม่เจอ: {e}")
            return

        url = info['url']
        title = info.get('title', 'Unknown title')
        duration_sec = info.get('duration', 0)
        duration_str = self.get_duration_str(duration_sec)
        webpage_url = info.get('webpage_url', None)
        thumbnail = info.get('thumbnail', None)

        # สร้าง source สำหรับเล่นเสียง
        source = discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

        # เล่นเพลง
        if voice_client.is_playing():
            voice_client.stop()

        voice_client.play(source)

        # สร้าง Embed สวย ๆ
        embed = discord.Embed(
            title=f"🎵 กำลังเล่นเพลง: {title}",
            description=f"⏳ ความยาว: {duration_str}",
            color=0x1DB954  # สีเขียว Spotify-like
        )
        if webpage_url:
            embed.url = webpage_url
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

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

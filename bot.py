import discord
from discord.ext import commands
import asyncio
from yt_dlp import YoutubeDL
import os

# --- 設定 ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# サーバーごとの再生情報
current_music = {}  # {guild_id: URL}
volume_dict = {}    # {guild_id: float} 音量情報

# --- ヘルパー関数 ---
def get_audio_source(url):
    """YouTube URLから直接音声URLを取得"""
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']

# --- コマンド ---
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"✅ **{channel.name}** に接続しました！")
        elif ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ **{channel.name}** に移動しました！")
        else:
            await ctx.send(f"既に **{channel.name}** に接続しています。")
    else:
        await ctx.send("⚠️ まずボイスチャンネルに参加してください。")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ボイスチャンネルから切断しました。")
        current_music.pop(ctx.guild.id, None)
        volume_dict.pop(ctx.guild.id, None)
    else:
        await ctx.send("⚠️ ボイスチャンネルに接続していません。")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("🛑 音楽を停止しました。")
        current_music.pop(ctx.guild.id, None)
    else:
        await ctx.send("⚠️ 再生中の音楽はありません。")

@bot.command()
async def music(ctx, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("⚠️ まずボイスチャンネルに参加してください。")
            return

    # 再生中の場合は停止
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    guild_id = ctx.guild.id
    current_music[guild_id] = url
    volume = volume_dict.get(guild_id, 0.5)  # デフォルト音量50%

    try:
        source_url = await asyncio.to_thread(get_audio_source, url)
    except Exception as e:
        await ctx.send(f"❌ URLから音声を取得できませんでした。\nエラー: `{e}`")
        current_music.pop(guild_id, None)
        return

    async def loop_music(voice_client, music_source_url, music_url):
        while current_music.get(guild_id) == music_url:
            try:
                audio_source = discord.FFmpegPCMAudio(music_source_url, options='-vn')
                voice_client.play(discord.PCMVolumeTransformer(audio_source, volume=volume))
            except Exception as e:
                print(f"再生中にエラー: {e}")
                break

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)

            if current_music.get(guild_id) != music_url:
                break

            await asyncio.sleep(0.5)

    bot.loop.create_task(loop_music(ctx.voice_client, source_url, url))
    await ctx.send(f"🎶 音楽を再生中 (ループ再生): <{url}>")

@bot.command()
async def volume(ctx, vol: int):
    """音量変更 0~100"""
    if ctx.voice_client is None:
        await ctx.send("⚠️ ボイスチャンネルに接続していません。")
        return
    if not 0 <= vol <= 100:
        await ctx.send("⚠️ 音量は0から100の間で指定してください。")
        return

    guild_id = ctx.guild.id
    volume_dict[guild_id] = vol / 100

    if ctx.voice_client.is_playing():
        # 再生中の音源の音量を即座に変更
        ctx.voice_client.source.volume = vol / 100

    await ctx.send(f"🔊 音量を **{vol}%** に設定しました。")

# --- Bot 起動 ---
bot.run(os.environ['DISCORD_TOKEN'])

import discord
import re
import requests
from env import TOKEN
from discord.ext.commands import Bot
from discord.ext import commands
from colorthief import ColorThief
import datetime

client = discord.Client()
bot = commands.Bot(command_prefix='>')
bot.remove_command('help')

baseAPI = "https://ctftime.org/api/v1"

@bot.event
async def on_ready():
    print(('<' + bot.user.name) + ' Online>')
    print(f"discord.py {discord.__version__}\n")
    await bot.change_presence(activity=discord.Game(name='>help'))


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command()
async def help(ctx, page=None):
    emb = discord.Embed(description="Upcoming CTFs", colour=4387968)
    emb.set_author(name='>ctftime upcoming')

    await ctx.channel.send(embed=emb)



@bot.command()
async def ctftime(ctx, cmd=None):
    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
    }
    
    if cmd == "upcoming":
        res = requests.get(f"{baseAPI}/events/", headers=headers)
        data = res.json()

        for num in range(3):

            ctf_title = data[num]['title']
            (ctf_start, ctf_end) = (data[num]['start'].replace('T', ' ').split('+', 1)[0] + ' UTC', data[num]['finish'].replace('T', ' ').split('+', 1)[0] + ' UTC')
            (ctf_start, ctf_end) = (re.sub(':00 ', ' ', ctf_start), re.sub(':00 ', ' ', ctf_end))
            dur_dict = data[num]['duration']
            (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
            ctf_link = data[num]['url']
            ctf_image = data[num]['logo']
            ctf_format = data[num]['format']
            ctf_place = data[num]['onsite']
            
            if ctf_place == False:
                ctf_place = 'Online'
            else:
                ctf_place = 'Onsite'

            f_color = int("478bbf", 16)
            embed = discord.Embed(title=ctf_title, description=ctf_link, color=f_color)
            
            if ctf_image != '':
                embed.set_thumbnail(url=ctf_image)
            #else:
                #embed.set_thumbnail(url=default_image)

            ctf_duration = f"{ctf_days} {'days' if int(ctf_days) != 1 else 'day'}, {ctf_hours} {'hours' if int(ctf_hours) != 1 else 'hour'}"
            embed.add_field(name='Duration', value=ctf_duration, inline=True)

            ctf_format = f"{ctf_place} {ctf_format}"
            embed.add_field(name='Format', value=ctf_format, inline=True)
            
            ctf_time_interval = f"{ctf_start} -> {ctf_end}"
            embed.add_field(name='─' * 30, value=ctf_time_interval, inline=True)

            await ctx.channel.send(embed=embed)

    elif "byteforce" in cmd.lower() or "byteforc3" in cmd.lower():
        res = requests.get(f"{baseAPI}/teams/71631/", headers=headers)
        data = res.json()
        year = str(datetime.datetime.now().year)

        name = data["name"]
        link = r"https://ctftime.org/team/71631"
        points = data["rating"][0][year]["rating_points"]
        place = data["rating"][0][year]["rating_place"]

        f_color = int("478bbf", 16)
        embed = discord.Embed(title=name, description=link, color=f_color)

        embed.add_field(name='Rating Points', value=f"{points} points", inline=True)
        embed.add_field(name='Rating Place', value=f"{place} place", inline=True)

        await ctx.channel.send(embed=embed)


    else:
        emb = discord.Embed(description="Upcoming CTFs", colour=4387968)
        emb.set_author(name='>ctftime upcoming')

        await ctx.channel.send(embed=emb)


bot.run(TOKEN)

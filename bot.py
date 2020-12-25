import discord
import re
import requests
from texttable import Texttable
import pandas as pd
from env import TOKEN
from discord.ext.commands import Bot
from discord.ext import commands
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
    emb = discord.Embed(description="Use >ctftime to get started", colour=4387968)

    await ctx.channel.send(embed=emb)


def get_table(events):
    rows = [row[1:3]+row[4::] for row in events]
    head = [['Place', 'Event', 'Points']] 
    table = head + rows

    t = Texttable()
    t.add_rows(table)

    return t.draw()


@bot.command()
async def ctftime(ctx, cmd=""):
    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
    }
    team_name , team_id , team_alias = "ByteForc3" , "71631" , "byteforce"

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

    elif team_name.lower() == cmd.lower() or team_alias.lower() == cmd.lower():
        res = requests.get(f"{baseAPI}/teams/{team_id}/", headers=headers)
        data = res.json()
        year = str(datetime.datetime.now().year)

        name = data["name"]
        link = f"https://ctftime.org/team/{team_id}"
        points = data["rating"][0][year]["rating_points"]
        place = data["rating"][0][year]["rating_place"]

        f_color = int("478bbf", 16)
        embed = discord.Embed(title=name, description=link, color=f_color)

        embed.add_field(name='Rating Points', value=f"{points} points", inline=True)
        embed.add_field(name='Rating Place', value=f"{place} place", inline=True)

        await ctx.channel.send(embed=embed)

    elif "rank" in cmd.lower():
        url  = f"https://ctftime.org/team/{team_id}"
        team_perf = requests.get(url , headers = headers)

        df = pd.read_html(team_perf.text, match = r"CTF points")[0]
        table = df.values.tolist()

        for row in table:                          
           row[4] = row[4].replace('*','')                  #cleaning table
        topEvents = sorted(table, key=lambda p:float(p[4]), reverse=True)[:10]
        table = get_table(topEvents)

        f_color = int("478bbf", 16)
        embed = discord.Embed(title = "List of Top Events", description=f"```css\n{table}```", color=f_color)

        await ctx.channel.send(embed = embed)

    else:
        description = """```ini
        [>ctftime upcoming]
        [>ctftime rank]
        [>ctftime byteforce]
        ```"""
        listCommand = ["upcoming", "rank", "ByteForc3"]
        description = '```ini\n{}```'.format("".join(f"[>ctftime {command}]\n" for command in listCommand))
        emb = discord.Embed(name = "ctftime Commands", description=f"Commands : \n{description}", colour=4387968)

        await ctx.channel.send(embed=emb)


bot.run(TOKEN)

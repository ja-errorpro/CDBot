import os

from discord.ext import tasks
# from discord_slash import cog_ext,SlashCommand, SlashContext
# from discord_slash.utils.manage_commands import create_choice, create_option
import json
import random
import interactions

from interactions.api.models import flags as FLAGS
from interactions.api.models import channel as ChannelAPI
from interactions.api.models import presence
from interactions.api.models import member
from interactions.ext.files import command_send

import sys

#from dotenv import load_dotenv

from async_timeout import timeout

#from bs4 import BeautifulSoup
#from commands import app

import sqlite3


net = sqlite3.connect('eco_system.db')
cur = net.cursor()  

with open('./config.json','r') as setting:
    config = json.load(setting)
    
with open('./tips.json','r',encoding='utf8') as tipsfile:
    global tips 
    tips = json.load(tipsfile)

# https://discord.com/api/oauth2/authorize?client_id=614466185156755475&permissions=8&scope=bot


prefix = config["prefix"]

act = presence.PresenceActivity(name="Made by 麻幻",type=0)
actstat = presence.ClientPresence(activities=[act],status='online',afk=False)

client = interactions.Client(
    token = config["token"],
    intents=FLAGS.Intents.ALL,
    presence=actstat)



MasterID = int(config["Admin"])
chanid = 728660343219290134


@client.event
async def on_ready():
    print('Now : ',client.me.name)
   
    global getMaster 
    getMaster = await interactions.get(client,interactions.User, object_id = MasterID)
    
    await getMaster.send("I am Online Now!") 
    guildlst = []
    for x in client.guilds:
        guildlst.append(x.name)
    print("Joined in ",guildlst)
    client._loop.create_task(update_tips())

    

    
@client.event
async def on_guild_join(guild):
    print(f"Join to {guild.name},ID: {guild.id}")

    
def rt():
    print('Restarting...')
    os.execv(sys.executable,['python']+sys.argv)




@client.command(name="restart",description="重新啟動機器人(最高管理指令)")
async def _restart(ctx):

    req = ""
    if ctx.guild is None:
        req = "A restart command has been executed in DM by "+str(ctx.user.username)
    else:
        req = "A restart command has been executed in "+ctx.guild.name + ": "+ ctx.channel.name + " by "+ctx.user.username
    if(ctx.user==getMaster):
        await getMaster.send(req + " (Approved)")
        await ctx.send("Restarting...")
        await rt()
    else:
        await getMaster.send(req + " (Denied)")
        await ctx.send(ctx.user)


#client.remove_command('help')



@tasks.loop(seconds=3600)
async def update_tips(): 
    try:
        tips = json.load(open('./tips.json','r',encoding='utf8')) 
        print("Updated Tips.")
    except:
        # admin = config["Admin"]
        # 728660343219290134
        await getMaster.send("警告 更新Tips發生錯誤！")
        


@client.event(name="on_message_create")
async def on_message(message):
    if message.author.id == client.me.id:
        return
    
    
    text = message.content
    chan = await message.get_channel()
    if client.me.guild_id is None :
        #img = interactions.File(filename="./assets/image/tips_0.jpg")
        #await message.reply(files=img)
        
        await getMaster.send('DM Message with '+str(message.author)+': '+message.content)

    if text.startswith('ping'):
        await chan.send('pong')
    elif '我婆' in text or '老婆' in text:
        await message.reply("醒醒, 你沒有老婆!")
    elif text.startswith('誰是大佬') or text.startswith('大佬是誰'):
        await chan.send('至少這個機器人的主人不是')
    elif '臭甲' in text or '甲甲' in text:
        ran = random.randint(0,100)
        if ran < 40:
            await message.reply("你是臭甲")
        
    elif '的機率' in text:
        ran = random.randint(0,100)
        output = str(ran) + '%' 
        await chan.send(output)
    elif '睡覺' in text:
        ran = random.randint(0,100)
        if ran < 30:
            await chan.send('睡屁起來嗨')
    elif '洗澡' in text:
        ran = random.randint(0,100)
        if ran < 75:
            await message.reply('嚕拉拉 嚕拉拉 嚕拉嚕拉勒')
    elif text.startswith('抽女友') or text.startswith('抽女朋友'):
        await message.reply('抽到你了!') 
    elif text == '喵嗚嗚':
        rans = random.choice(tips["text_list"])
        if isinstance(rans,dict):
            URL = list(rans.values())
            img = interactions.File(filename=URL[0])
            await chan.send(files=img)
        else:
            await chan.send(rans)
    elif text == '修理':
        await message.reply('你怎麼去不修理你的人生')
    elif text.startswith('幹'):
        ran = random.randint(0,100)
        if ran < 30:
            await message.reply('幹什麼幹，沒禮貌')
    elif '笑死' in text:
        ran = random.randint(0,100)
        if ran < 20:
            await message.reply('笑你媽 好笑嗎')
    elif text == '咚' or text == '咖' or text == '咔':
        ran = random.randint(0,100)
        if ran < 10:
            await message.reply('不可')
        elif ran < 30:
            await message.reply('可')
        else:
            await message.reply('良')
    elif ';Am I a ' in text:
        await message.reply(random.choice(['yes','no']))




if __name__ == '__main__':

    client.load("cog")
    client.load("eco")
    client.load("waifu")
    client.load("game_battle")
    client.load("dalle")
    
    client.start()

from discord.ext import commands,tasks
# from discord_slash import cog_ext,SlashCommand, SlashContext
# from discord_slash.utils.manage_commands import create_choice, create_option
import json
import random
import os
import sys

from dotenv import load_dotenv
import asyncio

from async_timeout import timeout
import requests
import aiohttp
import io
from bs4 import BeautifulSoup

import interactions

from interactions.api.models import flags as FLAGS
from interactions.api.models import channel as ChannelAPI
from interactions.api.models import presence
from interactions.api.models import member

with open('./config.json','r') as setting:
    config = json.load(setting)

class Waifu(interactions.Extension):
    def __init__(self,bot):
        self.bot = bot
    
    @interactions.extension_listener()
    async def on_ready(self):
        print("Waifu is ready")

    @interactions.extension_command(
        name="wifu",
        description="傳送一張老婆"
    )
    async def _wifu(self,ctx):
        await ctx.defer()
        #msg = await ctx.send("請稍候...")
        GetWifeUrl = requests.get("https://api.waifu.pics/sfw/waifu")
        GetWifeUrlJson = json.loads(GetWifeUrl.text)
        GetWife = GetWifeUrlJson["url"]
        await ctx.send(content=GetWife)
            
    @interactions.extension_command(
        name="neko",
        description="傳送一張貓圖"
    )
    async def _neko(self,ctx):
        await ctx.defer()
        #msg = await ctx.send("請稍候...")
        GetNekoUrl = requests.get("https://api.waifu.pics/sfw/neko")
        GetNekoUrlJson = json.loads(GetNekoUrl.text)
        GetNeko = GetNekoUrlJson["url"]
        await ctx.send(content=GetNeko)
        
    @interactions.extension_command(
        name="nsfw",
        description="傳送瑟瑟圖(無法在非限制級頻道使用)",
        dm_permission=False
    )
    async def _nsfw(self,ctx):
        await ctx.defer()


        if ctx.channel.nsfw == True:
            
            #msg = await ctx.send("請稍候...")
            GetNsfwUrl = requests.get("https://api.waifu.pics/nsfw/waifu")
            GetNsfwUrlJson = json.loads(GetNsfwUrl.text)
            GetNsfw = GetNsfwUrlJson["url"]
            await ctx.send(content=GetNsfw)
        else:
            await ctx.send("不可以在這裡瑟瑟")



def setup(bot):
    Waifu(bot)

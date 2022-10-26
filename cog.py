
from discord.ext import commands,tasks
#from discord_slash import cog_ext,SlashCommand, SlashContext
#from discord_slash.utils.manage_commands import create_choice, create_option
import json
import random

from dotenv import load_dotenv

from async_timeout import timeout
import requests
from bs4 import BeautifulSoup
#import logging
import interactions
from interactions.api.models import flags as FLAGS
from interactions.api.models import channel as ChannelAPI
from interactions.api.models import presence
from interactions.api.models import member


with open('./config.json','r') as setting:
    config = json.load(setting)

with open('./tips.json','r',encoding='utf8') as tipsfile:
    global tips 
    tips = json.load(tipsfile)

@tasks.loop(seconds=3600)
async def update_tips():
    try:
        tips = json.load(open('./tips.json','r',encoding='utf8'))
    except:
        pass

class Slash(interactions.Extension):


    
            
    def __init__(self,bot):
        self.bot = bot
        bot._loop.create_task(update_tips())
        
    @interactions.extension_command(
        name="dice",
        description="擲骰子",
        options=[
            interactions.Option(
                type=3,
                name="arg",
                description = "隨機擲出1~6點",
                required = False,
                choices=[
                    interactions.Choice(
                        name = "1~6",
                        value = "0"
                    ),
                    interactions.Choice(
                        name = "1~100",
                        value = "1"
                    ),
                    interactions.Choice(
                        name = "1~1000",
                        value = "2"
                    ),
                ],
            )
        ]
    )
    async def _dice(self,ctx,**args):
        if len(args)==0 or args['arg'] == '0':
            ran = random.randint(1,6)
            await ctx.send('擲出'+str(ran)+'點')
        elif args['arg'] == '1':
            ran = random.randint(1,100)
            await ctx.send('擲出'+str(ran)+'點')
        elif args['arg'] == '2':
            ran = random.randint(1,1000)
            await ctx.send('擲出'+str(ran)+'點')
            
    
    
    
    @interactions.extension_command(
        name="poker",
        description="抽一張撲克牌",
        options=[
            interactions.Option(
                name = "arg",
                description = "要不要鬼牌",
                required = False,
                type = 3,
                choices=[
                    interactions.Choice(
                        name = "Y",
                        value = "normal"
                    ),
                    interactions.Choice(
                        name = "N",
                        value = "nojoker"
                    ),
                ]
            )
        ]
    )   
    async def _poker(self,ctx,**args):
        shap = random.randint(1,4)
        joker = random.randint(1,54)
        num = str(random.randint(1,13))
        if len(args)==0 or args['arg']!='nojoker':
            if joker >= 53:
                await ctx.send("抽到鬼牌!")
            else:
                if shap == 1:
                    await ctx.send("抽到黑桃"+num)
                elif shap == 2:
                    await ctx.send("抽到紅心"+num)
                elif shap == 3:
                    await ctx.send("抽到方塊"+num)
                elif shap == 4:
                    await ctx.send("抽到梅花"+num)
        else:
            if shap == 1:
                await ctx.send("抽到黑桃"+num)
            elif shap == 2:
                await ctx.send("抽到紅心"+num)
            elif shap == 3:
                await ctx.send("抽到方塊"+num)
            elif shap == 4:
                await ctx.send("抽到梅花"+num)
                
                
    @interactions.extension_command(
        name="rps",
        description="跟我猜拳",
        options=[
            interactions.Option(
                name = "arg",
                description = "出拳",
                required = True,
                type = 3,
                choices=[
                    interactions.Choice(
                        name = "剪刀",
                        value = "剪刀"
                    ),
                    interactions.Choice(
                        name = "石頭",
                        value = "石頭"
                    ),
                    interactions.Choice(
                        name = "布",
                        value = "布"
                    ),
                ]
            )
        ]
    )              
    async def _rps(self,ctx,arg:str):
        if len(arg)<1 or (arg!='石頭' and arg!='剪刀' and arg!='布'):
            await ctx.send('錯誤的使用方式，請回報給我主人或查看c!help')
        else:
            ran = random.choice(['石頭','剪刀','布'])
            if arg == '石頭':
                if ran == '石頭':
                    await ctx.send('我猜石頭,我們平手!')
                elif ran == '剪刀':
                    await ctx.send('我猜剪刀,你贏了!')
                elif ran == '布':
                    await ctx.send('我猜布,你輸了!')
            elif arg == '剪刀':
                    if ran == '石頭':
                        await ctx.send('我猜石頭,你輸了!')
                    elif ran == '剪刀':
                        await ctx.send('我猜剪刀,我們平手!')
                    elif ran == '布':
                        await ctx.send('我猜布,你贏了!')
            elif arg == '布':
                if ran == '石頭':
                    await ctx.send('我猜石頭,你贏了!')
                elif ran == '剪刀':
                    await ctx.send('我猜剪刀,你輸了!')
                elif ran == '布':
                    await ctx.send('我猜布,我們平手!')
    

    @interactions.extension_command(name="ccn",description="獲取台灣疫情最新資訊")
    async def ccn(self,ctx):
        await ctx.send('正在獲取最新資訊...')
        source = "資料來源：衛福部疾病管制署"
        rq = requests.get("https://covid-19.nchc.org.tw/api/covid19?CK=covid-19@nchc.org.tw&querydata=4048",timeout=10)
        rq2 = requests.get("https://covid-19.nchc.org.tw/dt_005-covidTable_taiwan.php",timeout=10)
        
        soup = BeautifulSoup(rq2.text,"html.parser")
        rqjson = json.loads(rq.text)

        updatedate = rqjson[0]['a01'] # 更新日期
        TodayaddConfirm = rqjson[0]['a04'] # 今日合計送驗
        TodayaddDiag = rqjson[0]['a06'] # 今日新增確診
        CumDiag = soup.find("h1",class_="country_confirmed mb-1 text-success").text # 累計確診
        CumDeath = soup.find("h1",class_="country_deaths mb-1 text-dark").text # 累計死亡
        TodayaddDiagLocal = str(soup.find_all("span",class_="country_confirmed_percent")[1].text).split('本土病例 ')[1] # 本土確診
        CumDiagLocal = str(soup.find_all("span",class_="country_confirmed_percent")[0].text).split('本土病例 ')[1] # 本土累計
        TodayaddDeath = soup.find("span",class_="country_deaths_change").text # 今日新增死亡
        
        embed = interactions.Embed(title="疫情最新資訊 "+source,description="資料更新日期："+str(updatedate),color=0xB80000)
        embed.add_field(name="累計確診",value=str(CumDiag),inline=False)
        embed.add_field(name="本土累計確診",value=str(CumDiagLocal),inline=False)    
        embed.add_field(name="累計死亡",value=str(CumDeath),inline=False)
        embed.add_field(name="新增確診",value=str(TodayaddDiag),inline=False)
        embed.add_field(name="新增本土確診",value=str(TodayaddDiagLocal),inline=False)
        embed.add_field(name="新增死亡",value=str(TodayaddDeath),inline=False)
        embed.add_field(name="今日合計送驗",value=str(TodayaddConfirm),inline=False)
        await ctx.send(embeds=embed)

    @interactions.extension_command(name="help",
    description="查看幫助",
    options=[
        interactions.Option(
            name="page",
            description="選擇幫助頁面",
            required=True,
            type=4,
            choices=[
                interactions.Choice(
                    name = "1(/bal~/neko)",
                    value = 1
                ),
                interactions.Choice(
                    name = "2(/nextfeature~)",
                    value = 2
                )
            ]
        )
    ]
    )
    async def help(self,ctx,page):
        if page == 1:
            embed = interactions.Embed(title="幫助指令",description="第一頁",color=0x6036a4)
            embed.add_field(name="`/bal`",value="查看你的帳戶餘額",inline=False)
            embed.add_field(name="`/battle`",value="跟人戰鬥",inline=False)
            embed.add_field(name="`/battle-rank`",value="查看戰力排行榜",inline=False)
            embed.add_field(name="`/ccn`",value="獲取台灣疫情最新資訊，注意執行此指令才會重新載入最新資訊",inline=False)
            embed.add_field(name="`/daily`",value="每日簽到",inline=False)
            embed.add_field(name="`/dice [1~6|1~100|1~1000]`",value="擲骰子",inline=False)
            embed.add_field(name="`/give-money (User) (Amount)`",value="轉帳",inline=False)
            embed.add_field(name="`/help`",value="顯示這則訊息",inline=False)
            embed.add_field(name="`/info`",value="顯示戰鬥資訊",inline=False)
            embed.add_field(name="`/neko`",value="傳送一張貓圖(基於 Waifu.PICS API)",inline=False)
            
        elif page == 2:
            embed = interactions.Embed(title="幫助指令",description="第二頁",color=0x6036a4)
            embed.add_field(name="`/nextfeature`",value="查看我的主人將會教我什麼東西",inline=False)
            embed.add_field(name="`/poker [Y|N]`",value="抽一張撲克牌",inline=False)
            embed.add_field(name="`/reg`",value="註冊C幣帳戶",inline=False)
            embed.add_field(name="`/richest`",value="查看富豪榜",inline=False)
            embed.add_field(name="`/rps (剪刀|石頭|布)`",value="跟我猜拳",inline=False)
            embed.add_field(name="`/wifu`",value="傳送一張老婆(基於 Waifu.PICS API)",inline=False)
            embed.add_field(name="`喵嗚嗚`",value="獲取一些Tips，目前Tips數量："+str(len(tips["text_list"])),inline=False)
            embed.add_field(name="`咚/咖/咔`",value="太鼓達人",inline=False)
        await ctx.send(embeds=embed)
        

    @interactions.extension_command(name="nextfeature",description="查看我的學習規劃")
    async def _nf(self,ctx):
        embed = interactions.Embed(title="CDBot 未來規劃",description="更新時間：2022/10/22 15:30",color=0x00ff44)
        embed.add_field(name="1. Update my Library",value="A BIG UPDATE Comming Soon...",inline=False)
        embed.add_field(name="2. 增加更多Tips",value="學更多ㄍㄢˋㄏㄨㄚˋ",inline=False)
        embed.add_field(name="3. 簡易管理系統",value="給管理員方便",inline=False)
        await ctx.send(embeds=embed)
        

    
    
            
    
        
    
def setup(bot):
    #logging.basicConfig(level=logging.DEBUG)
    Slash(bot)
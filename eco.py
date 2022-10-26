
from discord.ext import tasks

import json
import random


from dotenv import load_dotenv

from async_timeout import timeout
import requests
from bs4 import BeautifulSoup

import sqlite3
import datetime
import time


import interactions

from interactions.api.models import flags as FLAGS
from interactions.api.models import channel as ChannelAPI
from interactions.api.models import presence
from interactions.api.models import member

with open('./config.json','r') as setting:
    config = json.load(setting)

with open('./tips.json','r',encoding='utf8') as tipsfile:
    tips = json.load(tipsfile)
    
    
net = sqlite3.connect('eco_system.db')
cur = net.cursor()  

@tasks.loop(seconds=3600)
async def update():
    net = sqlite3.connect('eco_system.db')
    cur = net.cursor() 

def get_bal(guild: str,user: str):
    try:

        cur.execute("SELECT balance FROM Clients WHERE guild=? AND client_name=?",(guild,user))
        rets = cur.fetchone()
        ret = int(rets[0])
        return ret
    except:
        return False

def set_balance(guild: str,user: str,bal):
    try:
        cur.execute("UPDATE Clients SET balance=? WHERE guild=? AND client_name=?", (bal,guild,user,))
        net.commit()
        return(True)
    except:
        return(False)

def init_acc(guild: str,user: str):
    try:
        cur.execute("INSERT INTO Clients VALUES(?,?,?,?)",(guild,user,48763,None))
        print(f"Created Account for {user} in {guild}")
        net.commit()
    except:
        return False

class Economy(interactions.Extension):
    def __init__(self,bot):
        self.bot = bot
        bot._loop.create_task(update())
    
    @interactions.extension_listener()
    async def on_ready(self):
        print("Economy System Loaded Succesfully")
    
    
    
    @interactions.extension_command(name="reg",description="註冊帳戶",dm_permission = False)
    async def _reg(self,ctx):
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        guild = str(ctx.guild.id)
        clientname = str(ctx.user.id)
        cur.execute("SELECT client_name FROM Clients WHERE guild=? AND client_name=?",(guild,clientname,))
        ret = cur.fetchall()
        if len(ret) == 0:
            cur.execute("INSERT INTO Clients VALUES(?,?,?,?)",(guild,clientname,48763,None))
            print('Created a account for '+clientname+ ' in '+guild)
            await ctx.send("已成功創建帳戶！你得到了48763 C幣作為初始獎勵！")
        else:
            await ctx.send("錯誤，你是否已擁有帳戶？")
        net.commit()
     
    @interactions.extension_command(
        name="bal",
        description="查看當前餘額",
        dm_permission = False,
        options=[
            interactions.Option(
                name = "target",
                description="查詢對象",
                required=False,
                type=6,
            )
        ]
    )
    async def _bal(self,ctx,**args):
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        usr = str(ctx.author.id)
        if len(args)!=0:
            usr = str(args['target'].id)
            if usr == '614466185156755475':
                cur.execute("SELECT * FROM Clients WHERE guild=?",(str(ctx.guild.id),))
                rets = cur.fetchall()
                sum = 0
                cnt = 0
                for i in rets:
                    sum += rets[cnt][2]
                    cnt+=1
                await ctx.send("此帳戶有"+str(sum)+" C幣(本伺服器總和)")
                return
        #print(ctx.guild.id)
        ret = get_bal(str(ctx.guild.id),usr)
        if ret is False:
            await ctx.send("找不到此帳戶，正在自動創建")
            init_acc(str(ctx.guild.id),usr)
            ret = get_bal(str(ctx.guild.id),usr)
            if ret != False:
                await ctx.send("已成功創建帳戶！你得到了48763 C幣作為初始獎勵！")
            else:
                await ctx.send("發生錯誤，請回報給我主人")
                return
            
        await ctx.send("此帳戶有"+str(ret)+" C幣")
    
    @interactions.extension_command(
        name="give-money",
        description="轉帳",
        dm_permission = False,
        options=[
            interactions.Option(
                name = "receiver",
                description="轉帳對象",
                required = True,
                type = 6,
            ),
            interactions.Option(
                name = "amount",
                description="金額",
                required = True,
                type = 4,
            )
        ],
        
        
    )
    async def _givemoney(self,ctx,receiver,amount):
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        if amount < 1:
            await ctx.send("請輸入大於0的整數")
        else:    
            balance = get_bal(str(ctx.guild.id),str(ctx.user.id))
            if balance is False:
                    await ctx.send("找不到此帳戶，正在自動創建")
                    init_acc(str(ctx.guild.id),str(ctx.user.id))
                    balance = get_bal(str(ctx.guild.id),str(ctx.user.id))
                    if balance != False:
                        await ctx.send("已成功創建帳戶！你得到了48763 C幣作為初始獎勵！")
                    else:
                        await ctx.send("發生錯誤，請回報給我主人")
                        return
            elif receiver.id == self.bot.me.id:
                newbal = int(balance/2)
                if balance-amount < 0:
                    await ctx.send("你輸入金額已超過你的餘額")
                else:
                    await ctx.send("感謝您送錢給我，那我就直接到你帳戶拿囉~~~")
                    sc = set_balance(str(ctx.guild.id),str(ctx.user.id),newbal)
                    embed = interactions.Embed(title="系統提示")
                    embed.add_field(name=str(ctx.user.username)+"的帳戶遭到駭客入侵！",value="餘額消失了一半！",inline=False)
                    embed.add_field(name="你只剩下",value=str(newbal)+" 元",inline=False)
                    await ctx.send(embeds=embed)
            
            else:
                rbal = get_bal(str(ctx.guild.id),str(receiver.id))
                if rbal is False:
                    await ctx.send("找不到對方帳戶，正在自動創建")
                    init_acc(str(ctx.guild.id),str(receiver.id))
                    rbal = get_bal(str(ctx.guild.id),str(receiver.id))
                    if rbal != False:
                        await ctx.send("已成功創建帳戶！得到了48763 C幣作為初始獎勵！")
                    else:
                        await ctx.send("發生錯誤，請回報給我主人")
                        return
                
                newbal = balance - amount
                if newbal < 0:
                    await ctx.send("你輸入金額已超過你的餘額")
                else:
                    rnewbal = rbal + amount
                    rec = set_balance(str(ctx.guild.id),str(receiver.id),rnewbal)
                    sc = set_balance(str(ctx.guild.id),str(ctx.user.id),newbal)
                    if rec is True and sc is True:
                        await ctx.send("轉帳成功，剩餘金額："+str(newbal))
                    else:
                        await ctx.send("發生錯誤，請回報給我主人")
    
    @interactions.extension_command(
        name="daily",
        description="領取每日獎勵",
        dm_permission = False
    )
    async def _daily(self,ctx):
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        ret = get_bal(str(ctx.guild.id),str(ctx.user.id))
        if ret is False:
            await ctx.send("找不到此帳戶，正在自動創建")
            init_acc(str(ctx.guild.id),str(ctx.user.id))
            ret = get_bal(str(ctx.guild.id),str(ctx.user.id))
            if ret != False:
                await ctx.send("已成功創建帳戶！你得到了48763 C幣作為初始獎勵！")
            else:
                await ctx.send("發生錯誤，請回報給我主人")
                return

        cur.execute("SELECT last_daily FROM Clients WHERE guild=? AND client_name=?",(str(ctx.guild.id),str(ctx.user.id)))
        rets = cur.fetchone()
            #print(rets[0])
        if rets[0] == None:
            price = random.randint(100,1000)
            newbal = price + ret
            ld = datetime.date.today()
            cur.execute("UPDATE Clients SET last_daily=? WHERE guild=? AND client_name=?",(ld,str(ctx.guild.id),str(ctx.user.id)))
            cur.execute("UPDATE Clients SET balance=? WHERE guild=? AND client_name=?",(newbal,str(ctx.guild.id),str(ctx.user.id)))
            net.commit()
            await ctx.send("你獲得了每日獎勵 "+str(price)+" 元\n現在你有 "+str(newbal)+" C幣")
        elif (datetime.date.today()-datetime.date.fromisoformat(str(rets[0]))).days > 0:
            price = random.randint(100,1000)
            newbal = price + ret
            ld = datetime.date.today()
            cur.execute("UPDATE Clients SET last_daily=? WHERE guild=? AND client_name=?",(ld,str(ctx.guild.id),str(ctx.user.id)))
            cur.execute("UPDATE Clients SET balance=? WHERE guild=? AND client_name=?",(newbal,str(ctx.guild.id),str(ctx.user.id)))
            net.commit()
            await ctx.send("你獲得了每日獎勵 "+str(price)+" 元\n現在你有 "+str(newbal)+" C幣")
        else:
            await ctx.send("你已經領取過每日獎勵了，請明天再來")
                    
    @interactions.extension_command(
        name="richest",
        description="查看誰最有錢",
        dm_permission = False
    )
    async def _richest(self,ctx):
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        cur.execute("SELECT * FROM Clients WHERE guild=? ORDER BY balance DESC LIMIT 10",(str(ctx.guild.id),))
        rets = cur.fetchall()
        embed = interactions.Embed(title=":trophy:富豪榜:trophy:")
        cnt = 0
        authorinlist = False
        for i in rets:
            rk = cnt+1
            if rets[cnt][1] == str(ctx.user.id):
                authorinlist = True
            #getName = str((self.bot.get_user(int(rets[cnt][1]))))
            getName = str((await interactions.get(self.bot,interactions.User,object_id=int(rets[cnt][1]))).username)
            if getName == "None":
                getName = "無效用戶"
            if cnt == 0:
                embed.add_field(name=":first_place:"+getName,value=rets[cnt][2],inline=False)
            elif cnt == 1:
                embed.add_field(name=":second_place:"+getName,value=rets[cnt][2],inline=False)
            elif cnt == 2:
                embed.add_field(name=":third_place:"+getName,value=rets[cnt][2],inline=False)
            else:
                embed.add_field(name=str(rk)+". "+getName,value=rets[cnt][2],inline=False)
            cnt += 1
            
        await ctx.send(embeds=embed) 


    @interactions.extension_command(
        name="set-money",
        description="設定用戶餘額(行政指令)",
        dm_permission = False,
        default_member_permissions=8,
        options=[
            interactions.Option(
                name="user",
                description="設定用戶",
                required=True,
                type=6
            ),
            
            interactions.Option(
                name="amount",
                description="設定餘額",
                required=True,
                type=4
            ),

        ]
    )
    async def _setmoney(self,ctx,user,amount):   
        if ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
            return
        balance = get_bal(str(ctx.guild.id),str(user.id))
        if balance is False:
            await ctx.send("找不到此帳戶，正在自動創建")
            init_acc(str(ctx.guild.id),str(user.id))
            balance = get_bal(str(ctx.guild.id),str(user.id))
            if balance != False:
                await ctx.send("已成功創建帳戶！得到了48763 C幣作為初始獎勵！")
            else:
                await ctx.send("發生錯誤，請回報給我主人")
                return
            

        newbal = amount
        rec = set_balance(str(ctx.guild.id),str(user.id),newbal)
        if rec is True:
            await ctx.send("已成功設定帳戶餘額："+str(newbal)+" 元")
        else:
            await ctx.send("發生錯誤，請回報給我主人")
              
    @_setmoney.error
    async def _setmoney_error(self,ctx,error):
        if isinstance(error,AttributeError) and ctx.guild is None:
            await ctx.send("你不能在這裡使用經濟系統")
        else:
            await ctx.send(f"執行時發生 {error} 錯誤，請回報給我主人或查看/help")
    
    
        
def setup(bot):
    cur.execute("CREATE TABLE IF NOT EXISTS Clients(guild TEXT,client_name TEXT,balance INTEGER,last_daily)")
    Economy(bot)
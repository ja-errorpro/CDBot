
from discord.ext import tasks

import json
import random
import sys
from dotenv import load_dotenv
import asyncio
import functools
import itertools
import math
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

def set_balance(guild: str,user: str,bal: int):
    try:
        cur.execute("UPDATE Clients SET balance=? WHERE guild=? AND client_name=?", (bal,guild,user,))
        net.commit()
        return(True)
    except:
        return(False)
        
def get_info(guild: str,user: str):
    try:

        cur.execute("SELECT min_damage, max_damage, min_defense, max_defense,wins,ranks FROM Battle WHERE guild=? AND client_name=?",(guild,user))
        rets = cur.fetchone()
        
        return list(rets)
    except:
        return False

def set_info(guild: str,user: str,InfoList):
    try:
        cur.execute("UPDATE Battle SET min_damage=?, max_damage=?, min_defense=?, max_defense=?,wins=?,ranks=? WHERE guild=? AND client_name=?", (InfoList[0],InfoList[1],InfoList[2],InfoList[3],InfoList[4],InfoList[5],guild,user,))
        net.commit()
        return(True)
    except:
        return(False)        
        
        
def init_acc(guild: str,user: str):
    try:
        cur.execute("INSERT INTO Battle VALUES(?,?,?,?,?,?,?,?)",(guild,user,0,10,0,10,0,0))
        print(f"Created battle value for {user} in {guild}")
        net.commit()
    except:
        return False
# Rankup require wins: 5,10,20,35,55,80,...
rankup_require = [5,10,15,20,25,35,55,80,105,125,150,175,200,225,250,300,350,400,450,500,560,620,780,840,900,1000,1100,1200,1300,1400,1500,1700,1900,2100,
    2300,2500,2750,3000,3250,3500,3800,4100,4400,4700,5000,5350,5700,6050,6450,6850
    ]

def rankup(InfoList):
    try:
        InfoList[5]+=1
        InfoList[0]+=random.randint(20,40)
        InfoList[1] += random.randint(20,50)
        InfoList[2] += random.randint(20,40)
        InfoList[3] += random.randint(20,50)
        if InfoList[1] - InfoList[0] < 0:
            swap(InfoList[1] , InfoList[0])
        if InfoList[1] - InfoList[0] < 10:
            InfoList[1] += 10
        if InfoList[3] - InfoList[2] < 0:
            swap(InfoList[3] , InfoList[2])
        if InfoList[3] - InfoList[2] < 10:
            InfoList[3] += 10
        return InfoList
    except:
        return False

attack_skills = ["降維打擊","龜派氣功","紅蓮斬","狂戰士","電擊","海放全場","燕返","神羅天征","獻祭",
    "真正死亡","完美戰士","攻擊強化","幽冥即殺","精神混亂","地獄深淵","隕石","冰氣","穿透","迷惑",
    "力場控制","歐拉","擊退","打飛","抗性弱化","核打擊","星爆氣流斬","暴怒","瘴氣","原始之力",
    "霹靂卡霹靂拉拉 波波力那貝貝魯多 拍拍砰呸 噗哇噗哇噗 帕美魯克拉魯克 拉哩摟哩波噴 噗魯魯噗魯 發咪發咪發"
    ]
defence_skills = ["絕對鋼壁","物理抗性","絲血一擊","大盾","攻擊弱化","銅壁","以柔克剛","閃避","力場控制",
    "坦克","瞬間移動","傳送門","痛覺無效","再生","精準降低","抗性強化","神羅天征","傷害轉移","最好的防禦就是進攻",
    "拉麵神的守護","瘴氣","自動防禦","全反射","陷阱","力量超負荷","幻影","飛行","分身",
    "霹靂卡霹靂拉拉 波波力那貝貝魯多 拍拍砰呸 噗哇噗哇噗 帕美魯克拉魯克 拉哩摟哩波噴 噗魯魯噗魯 發咪發咪發"
    ]

class Battle(interactions.Extension):
    def __init__(self,bot):
        self.bot = bot
        bot._loop.create_task(update())
    
    @interactions.extension_listener()
    async def on_ready(self):
        print("Game Battle System Loaded Succesfully")
        
    @interactions.extension_command(
        name="info",
        description="查看戰鬥資訊",
        dm_permission = False,
        options=[
            interactions.Option(
                name = "args",
                description="對方",
                required = False,
                type = 6,
            ),
        ],
    )
    async def _info(self,ctx,**args):
        

        id = str(ctx.author.id)
        if len(args) != 0:
            id = str(args['args'].id)
        if id == 614466185156755475:
            embed = discord.Embed(title=str(self.bot.get_user(614466185156755475))+"的戰鬥資訊")
            embed.add_field(name="等級",value="OverflowError",inline=False)
            embed.add_field(name="攻擊力",value="OverflowError",inline=False)
            embed.add_field(name="防禦力",value="OverflowError",inline=False)
            embed.add_field(name="勝場數",value="OverflowError",inline=False)
            await ctx.send(embed=embed)
            return            
        usr = str(id)
        guild = str(ctx.guild.id)
        
        ret = get_info(guild,usr)
        if ret is False:
            init_acc(guild,usr)
            ret = get_info(guild,usr)
            if ret is False:
                await ctx.send("此指令發生錯誤，請通知我主人")
                return
        embed = discord.Embed(title=str(self.bot.get_user(int(id)))+"的戰鬥資訊")
        embed.add_field(name="等級",value=str(ret[5]),inline=False)
        embed.add_field(name="攻擊力",value=str(ret[0])+"~"+str(ret[1]),inline=False)
        embed.add_field(name="防禦力",value=str(ret[2])+"~"+str(ret[3]),inline=False)
        embed.add_field(name="勝場數",value=str(ret[4]),inline=False)
        await ctx.send(embed=embed)
    
    @interactions.extension_command(
        name="battle",
        description="跟人單挑",
        dm_permission = False,
        options=[
            interactions.Option(
                name = "target",
                description="對方",
                required = True,
                type = 6,
            ),
        ],
    )
    async def _battle(self,ctx,target):

        guild = str(ctx.guild.id)
        usr = str(ctx.author.id)
        usr_info = get_info(guild,usr)
        if usr_info is False:
            init_acc(guild,usr)
            usr_info = get_info(guild,usr)
        targetID = str(target.id)
        target_info = get_info(guild,targetID)
        if targetID == self.bot.me.id:
            await ctx.send(f"<@{ctx.author.id}> 對 <@{target.id}> 發起挑戰")
            time.sleep(1)
            await ctx.send(f"<@{self.bot.me.id}> 使出獨有技能：超越時間，成為攻擊方")
            k = random.choice(attack_skills)
            time.sleep(1)
            await ctx.send(f"<@{self.bot.me.id}> 使出技能："+k+"，對其造成 998244353214748364732767... 點傷害")
            time.sleep(1)
            await ctx.send(f"<@{ctx.author.id}> 以 0 點防禦力擋下")
            time.sleep(1)
            await ctx.send(f"<@{self.bot.me.id}> 獲勝")
            return
        elif target_info is False:
            init_acc(guild,targetID)
            target_info = get_info(guild,targetID)
        who_quick = random.randint(0,1)
        await ctx.send(f"<@{ctx.author.id}> 對 <@{target.id}> 發起挑戰")
        time.sleep(1)
        if who_quick == 0:
            await ctx.send(f"<@{ctx.author.id}> 快了一截，成為攻擊方")
            time.sleep(1)
            a = random.randint(usr_info[0],usr_info[1])
            b = random.randint(target_info[2],target_info[3])
            a_skill_rate = random.randint(1,100)
            b_skill_rate = random.randint(1,100)
            if a_skill_rate < usr_info[5]+1:
                r = float(random.randint(10,50))
                a = int(a*r/100)+a
                await ctx.send(f"<@{ctx.author.id}> 使出技能："+random.choice(attack_skills)+"，增加"+str(int(r))+"% 傷害")
                time.sleep(1)
            if b_skill_rate < target_info[5]+1:
                r = float(random.randint(10,50))
                b = int(b*r/100)+b
                await ctx.send(f"<@{target.id}> 使出技能："+random.choice(defence_skills)+"，增加"+str(int(r))+"% 防禦")
                time.sleep(1)
            await ctx.send(f"<@{ctx.author.id}> 對其造成 "+str(a)+" 點傷害")
            time.sleep(1)
            await ctx.send(f"<@{target.id}> 以 "+str(b)+" 點防禦擋下")
            time.sleep(1)
            if a > b:
                await ctx.send(f"<@{ctx.author.id}> 獲勝")
                usr_info[4] += 1
                if usr_info[4] in rankup_require:
                    usr_info = rankup(usr_info)
                    await ctx.send(f"<@{ctx.author.id}> 升級了！")
                set_info(guild,usr,usr_info)
            elif a<b:
                await ctx.send(f"<@{target.id}> 獲勝")
                target_info[4] += 1
                if target_info[4] in rankup_require and target.bot == False:
                    target_info = rankup(target_info)
                    await ctx.send(f"<@{target.id}> 升級了！")
                set_info(guild,targetID,target_info)
            else:
                await ctx.send("兩人沒有分出勝負")
                
        else:
            await ctx.send(f"<@{target.id}> 快了一截，成為攻擊方")
            time.sleep(1)
            a = random.randint(usr_info[2],usr_info[3])
            b = random.randint(target_info[0],target_info[1])
            a_skill_rate = random.randint(1,1000)
            b_skill_rate = random.randint(1,1000)
            
            if b_skill_rate < target_info[5]+1:
                r = float(random.randint(10,50))
                b = int(b*r/100)+b
                await ctx.send(f"<@{target.id}> 使出技能："+random.choice(attack_skills)+"，增加"+str(int(r))+"% 傷害")
                time.sleep(1)
            if a_skill_rate < usr_info[5]+1:
                r = float(random.randint(10,50))
                a = int(a*r/100)+a
                await ctx.send(f"<@{ctx.author.id}> 使出技能："+random.choice(defence_skills)+"，增加"+str(int(r))+"% 防禦")
                time.sleep(1)
            await ctx.send(f"<@{target.id}> 對其造成 "+str(b)+" 點傷害")
            time.sleep(1)
            await ctx.send(f"<@{ctx.author.id}> 以 "+str(a)+" 點防禦力擋下")
            time.sleep(1)
            if a > b:
                await ctx.send(f"<@{ctx.author.id}> 獲勝")
                usr_info[4] += 1
                if usr_info[4] in rankup_require:
                    usr_info = rankup(usr_info)
                    await ctx.send(f"<@{ctx.author.id}> 升級了！")
                set_info(guild,usr,usr_info)
            else:
                await ctx.send(f"<@{target.id}> 獲勝")
                target_info[4] += 1
                if target_info[4] in rankup_require and target.bot == False:
                    target_info = rankup(target_info)
                    
                    await ctx.send(f"<@{target.id}> 升級了！")
                set_info(guild,targetID,target_info)  
        
        #await ctx.send("Test Success")
    
    @_battle.error
    async def _battle_error(self,ctx,error):
        time.sleep(5)
        await ctx.send(f"執行時發生 {error} 錯誤，請回報給我主人或查看/help")
    

        
    @interactions.extension_command(
        name="battle-rank",
        description="查看戰力前十排行榜",
        dm_permission = False
    )
    async def _battle_rank(self,ctx):

        cur.execute("SELECT * FROM battle WHERE guild=? ORDER BY wins DESC, ranks DESC LIMIT 10",(str(ctx.guild.id),))
        rets = cur.fetchall()
        embed = interactions.Embed(title=":trophy:戰力榜:trophy:")
        cnt = 0
        authorinlist = False
        for i in rets:
            rk = cnt+1
            if rets[cnt][1] == str(ctx.author.id):
                authorinlist = True
            getName = str(await interactions.get(self.bot,interactions.User,object_id=int(rets[cnt][1])))
            if getName == "None":
                getName = "無效用戶"
            if cnt == 0:
                embed.add_field(name=":first_place:"+getName,value="勝場: "+str(rets[cnt][6])+" 等級: "+str(rets[cnt][7]),inline=False)
            elif cnt == 1:
                embed.add_field(name=":second_place:"+getName,value="勝場: "+str(rets[cnt][6])+" 等級: "+str(rets[cnt][7]),inline=False)
            elif cnt == 2:
                embed.add_field(name=":third_place:"+getName,value="勝場: "+str(rets[cnt][6])+" 等級: "+str(rets[cnt][7]),inline=False)
            else:
                embed.add_field(name=str(rk)+". "+getName,value="勝場: "+str(rets[cnt][6])+" 等級: "+str(rets[cnt][7]),inline=False)
            cnt += 1
            
        await ctx.send(embeds=embed) 
    
    @interactions.extension_command(
        name="set-battle",
        description="設定戰鬥資訊(行政指令)",
        dm_permission = False,
        default_member_permissions=8,
        options=[
            interactions.Option(
                name="index",
                description="設定項目",
                required=True,
                type=3,
                choices=[
                    interactions.Choice(
                        name = "damage",
                        #description="設定傷害區間",
                        value="0",
                    ),
                    interactions.Choice(
                        name = "defence",
                        #description="設定防禦區間",
                        value="1",
                        
                    ),
                    interactions.Choice(
                        name = "wins",
                        #description="設定勝場數",
                        value="2",
                        
                    ),
                    interactions.Choice(
                        name = "rank",
                        #description="設定等級",
                        value="3",
                    ),

                ]
            ), 
            interactions.Option(
                name="user",
                description="設定對象",
                required=True,
                type=6
            ),
            interactions.Option(
                name="args",
                description="設定數值，輸入數字或區間(格式: [x,y] )",
                required=True,
                type=3
            )
        ],
    )
    async def _setbattle(self,ctx,index,user,args):

        usrinfo = get_info(str(ctx.guild.id),str(user.id))
        if usrinfo is False:
            await ctx.send("未發現用戶")
        else:
            if index == "0":
                if len(args)<5:
                    await ctx.send("格式錯誤，應為非負整數 [最小值,最大值] : "+args)
                s = args.split(',')
                a = s[0][1:]
                b = s[1].split(']')[0]
                if not a.isdecimal() or not b.isdecimal() or int(a)<0 or int(b)<0:
                    await ctx.send("格式錯誤，應為非負整數 [最小值,最大值] : "+a + " "+ b)
                    return
                usrinfo[0] = int(a)
                usrinfo[1] = int(b)
                if set_info(str(ctx.guild.id),str(user.id),usrinfo):
                    await ctx.send("設定完成")
                else:
                    await ctx.send("設定失敗")
            elif index == "1":
                if len(args)<5:
                    await ctx.send("格式錯誤，應為非負整數 [最小值,最大值] : "+args)
                s = args.split(',')
                a = s[0][1:]
                b = s[1].split(']')[0]
                if not a.isdecimal() or not b.isdecimal() or int(a)<0 or int(b)<0:
                    await ctx.send("格式錯誤，應為非負整數 [最小值,最大值] : "+a + " "+ b)
                    return
                usrinfo[2] = int(a)
                usrinfo[3] = int(b)
                if set_info(str(ctx.guild.id),str(user.id),usrinfo):
                    await ctx.send("設定完成")
                else:
                    await ctx.send("設定失敗")
            elif index == "2":
                if not args.isdecimal() or int(args)<0 :
                    await ctx.send("格式錯誤，應為非負整數 : "+args)
                    return
                #print(len(usrinfo))
                usrinfo[4] = int(args)
                
                if set_info(str(ctx.guild.id),str(user.id),usrinfo):
                    await ctx.send("設定完成")
                else:
                    await ctx.send("設定失敗")
            elif index == "3":
                if not args.isdecimal() or int(args)<0 :
                    await ctx.send("格式錯誤，應為非負整數 : "+args)
                    return
                usrinfo[5] = int(args)
                if set_info(str(ctx.guild.id),str(user.id),usrinfo):
                    await ctx.send("設定完成")
                else:
                    await ctx.send("設定失敗")
            else:
                await ctx.send("指令格式錯誤")
    @_setbattle.error
    async def _setbattle_error(self,ctx,error):
        if isinstance(error,AttributeError) and ctx.guild is None :
            await ctx.send("你不能在這裡使用戰鬥系統")
        else:
            await ctx.send(f"執行時發生 {error} 錯誤，請回報給我主人或查看/help")    
    
        
def setup(bot):
    cur.execute("""CREATE TABLE IF NOT EXISTS Battle
        (guild TEXT,
        client_name TEXT,
        min_damage INTEGER,
        max_damage INTEGER,
        min_defense INTEGER, 
        max_defense INTEGER,
        wins INTEGER,
        ranks INTEGER)""")
    
    Battle(bot)
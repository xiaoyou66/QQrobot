# -*- coding: utf-8 -*-
import json
from typing import Optional
from aiocqhttp.message import escape

import re,configparser
import MySQLdb
from .robot import xiaoi_bot
from ..keyword import addreplay,download

import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand



# 注册一个仅内部使用的命令，不需要 aliases(这里就是不加命令时调用的方法)
@on_command('tuling')
async def tuling(session: CommandSession):
    message = session.get('message')
    # 这里来简单的替换内容
    await session.send(message)


# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@tuling.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    QQ = session.ctx['user_id']
    #await session.send("调试中")
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        #await session.send("第一次运行"+stripped_arg)
        if stripped_arg:

            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 通过封装的函数获取图灵机器人的回复
            reply = await call_tuling_api(session,stripped_arg)
            if reply:
                # 如果调用机器人成功，得到了回复，则转义之后发送给用户
                # 转义会把消息中的某些特殊字符做转换，以避免 酷Q 将它们理解为 CQ 码
                session.state['message'] = escape(reply)
                #await session.send(escape(reply))
            else:
                # 先把关键词存进去
                sql = "UPDATE chat SET temp='" + stripped_arg + "' WHERE QQ='" + str(QQ) + "'"
                sql_dml(sql)
                await session.pause("[CQ:at,qq=" + str(QQ) + "]对不起，小白不知道怎么回答，我应该怎么回答呢？(要以说为开头哦，如果需要发图片的话直接回复图片即可)")
                # 如果调用失败，或者它返回的内容我们目前处理不了，发送无法获取图灵回复时的「表达」
        else:
            await session.send("[CQ:at,qq=" + str(QQ) + "]有事可以直接用小白加上你想对我说的话就可与了哦，我不是小爱同学，不需要唤醒")
            session.finish()
        return

    if stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        if stripped_arg.startswith("说") or "image" in stripped_arg:
            sql="SELECT temp FROM chat WHERE QQ='"+str(QQ)+"'"
            result=sql_dql(sql)
            if "image" in stripped_arg or 'bface' in stripped_arg:
                if 'bface' in stripped_arg:
                    file = stripped_arg
                else:
                    file = download(stripped_arg[stripped_arg.find("url=") + 4:-1])
                    file = "[CQ:image,file=face/" + file + "]"
                key=result[0][0]+"-"+file
            else:
                key=result[0][0]+"-"+stripped_arg[1:]
            if addreplay(key):
                await session.send("[CQ:at,qq=" + str(QQ) + "]小白已成功学习到该回答！")
                session.finish()
                return
            # # 先找关键词
            # sql = "SELECT lastchat FROM chat WHERE QQ='" + str(QQ) + "'"
            # result = sql_dql(sql)
            # file = result[0][0][1:] + "-" + file
        else:
            await session.send("[CQ:at,qq=" + str(QQ) + "]已忽略该回复")
            session.finish()
            return


@on_natural_language
async def _(session: NLPSession):
    # 这里会保留所有的会话消息
    message= session.msg.strip()
    # 确保任何消息都在且仅在其它自然语言处理器无法理解的时候使用 tuling 命令
    return IntentCommand(60.0, 'tuling', current_arg=message)


async def call_tuling_api(session: CommandSession, text: str) -> Optional[str]:
    # 调用图灵机器人的 API 获取回复
    if not text:
        return None
    try:
        data=getconfig()
        bot = xiaoi_bot(data["key"],data['secret'] )
        data = bot.GetResponse(text, "123")
        data = re.sub(r'\[.*?\]', "", data)
        # 这里把换替换
        if(data.strip()=="默认回复" or data.strip()=="主人还没有给我设置这类话题的回复，你帮我悄悄的告诉他吧！"):
            return None
        else:
            return data.strip()
    except Exception:
        return None


#读取配置
def getconfig():
    data={}
    config = configparser.ConfigParser()
    config.read('config.ini',encoding='utf-8')
    data["ip"] = config.get('datebase','ip')
    data["user"] = config.get('datebase','user')
    data["passwd"] = config.get('datebase','passwd')
    data["db"] = config.get('datebase','db')
    data["port"] = config.get('datebase','port')
    data["qq"] = config.get('master','QQ')
    data["key"] = config.get('irobot','key')
    data['secret'] = config.get('irobot','Secret')
    # print(data)
    return data


#把数据库的操作函数都封装到一个函数里面，避免麻烦
def sql_dql(sql):
    data = getconfig()
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"],db=data["db"], charset='utf8')
    cursor = db.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        result = cursor.fetchall()
        db.close()
        return result
    except:
        return {}


def sql_dml(sql):
    data = getconfig()
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"],db=data["db"], charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        db.close()
        return 1
    except:
        db.rollback()
        db.close()
        return 0
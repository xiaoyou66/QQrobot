# 关键词特定回复，防止某人乱搞
# -*- coding: utf-8 -*-
import json
import MySQLdb
import random,time,configparser
import os
import requests
# from .robot import xiaoi_bot
from ..voice.sendData import AddVoice

import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

# 注册一个仅内部使用的命令，不需要 aliases(这里就是不加命令时调用的方法)
@on_command('keyword')
async def keyword(session: CommandSession):
    # 获取可选参数，这里如果没有 message 参数，命令不会被中断，message 变量会是 None
    QQ = session.ctx['user_id']
    # message = session.state.get('message')
    message = session.get('message')
    # 这里来简单的替换内容
    message = message.replace("@", "[CQ:at,qq=" + str(QQ) + "]")

    message = message.replace("\\n", "\n")
    await session.send(message)
    # 通过封装的函数获取图灵机器人的回复


@keyword.args_parser
async def _(session: CommandSession):
    # 命令解析器用于将用户输入的参数解析成命令真正需要的数据
    # 去掉消息首尾的空白符
    QQ = session.ctx['user_id']
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 这里我们进行判断，是否是学习模式
            if stripped_arg == '学习' or stripped_arg.startswith("编辑关键词"):
                # 先判断用户是否在数据库
                sql = "SELECT QQ FROM believe WHERE QQ='" + str(QQ) + "'"
                if sql_dql(sql):
                    if stripped_arg=="学习":
                        await session.pause("[CQ:at,qq=" + str(QQ) + "]回复“关键词-回复内容”即可学习到这个内容（多个回复可以用@@分割）\n小提示：支持表情，换行，还有‘@’表示@这个人")
                    else:
                        key=stripped_arg[5:]
                        if key:
                            sql = "SELECT thekey,replay FROM cKeyword WHERE thekey LIKE'%"+key+"%'"
                            result=sql_dql(sql)
                            if result:
                                senddata=""
                                temp=""
                                for i in range(0,len(result)):
                                    senddata+=(str(i)+"."+result[i][0]+"\n")
                                    temp+=result[i][0]+"-"
                                senddata+="回复对应数字即可删除关键词"
                                # 这里负责把内容暂时存起来
                                sql="UPDATE chat SET temp='"+temp+"' WHERE QQ='"+str(QQ)+"'"
                                sql_dml(sql)
                                await session.pause(senddata)
                            else:
                                await session.send("[CQ:at,qq=" + str(QQ) + "]没有找到关键词，换一个关键词试试")
                                session.finish()
                        else:
                            await session.send("[CQ:at,qq=" + str(QQ) + "]关键词为空，请在编辑关键词后面加上关键词")
                            session.finish()
                else:
                    await session.send("[CQ:at,qq=" + str(QQ) + "]抱歉，你不在信任名单")
                    session.finish()
            elif stripped_arg == '信任':
                data=getconfig()
                if QQ == int(data['qq']):
                    await session.pause("回复QQ号即可添加")
                else:
                    await session.send("[CQ:at,qq=" + str(QQ) + "]抱歉，你没有这个权限")
                    session.finish()
            elif stripped_arg.startswith("#") or stripped_arg.startswith("删除"):
                # 先判断用户是否在数据库
                sql = "SELECT QQ FROM believe WHERE QQ='" + str(QQ) + "'"
                if sql_dql(sql):
                    #判断是否是语音回复
                    if stripped_arg.startswith("##"):
                        key=(stripped_arg[2:]).split("-")
                        #await session.send("关键词为:"+key[1])
                        result=await AddVoice(key[1])
                        if result:
                            if addreplay(key[0]+"-"+result):
                                await session.send("[CQ:at,qq=" + str(QQ) + "]添加语音回复成功")
                                session.finish()
                                return
                        await session.send("[CQ:at,qq=" + str(QQ) + "]添加失败")
                        return
                    elif stripped_arg.startswith("删除"):
                        #await session.send("删除")
                        sql="SELECT keyDelete FROM chat WHERE QQ='"+str(QQ)+"'"
                        result=sql_dql(sql)
                        if result:
                            result=result[0][0].split("-")
                            sql="SELECT replay FROM cKeyword WHERE thekey='"+result[0]+"'"
                            qdata=sql_dql(sql)
                            if qdata:
                                replay=qdata[0][0].replace(result[1]+"@@","")
                                if replay.strip():
                                    sql="UPDATE cKeyword SET replay='"+replay+"' WHERE thekey='"+result[0]+"'"
                                else:
                                    sql="DELETE FROM cKeyword WHERE thekey='"+result[0]+"'"
                                if sql_dml(sql):
                                    await session.send("[CQ:at,qq=" + str(QQ) + "]已删除回复:"+result[1])
                                else:
                                    await session.send("[CQ:at,qq=" + str(QQ) + "]删除失败")
                            else:
                                await session.send("[CQ:at,qq=" + str(QQ) + "]查询结果为空")
                        else:
                            await session.send("[CQ:at,qq=" + str(QQ) + "]没有找到这个关键词")
                        session.finish()
                    else:
                        temp=stripped_arg[1:]
                        sql = "UPDATE chat SET temp='" + temp + "' WHERE QQ='" + str(QQ) + "'"
                        sql_dml(sql)
                        await session.pause("[CQ:at,qq=" + str(QQ) + "]关键词为:"+temp+" 请回复图片")
                else:
                    await session.send("[CQ:at,qq=" + str(QQ) + "]抱歉，你不在信任名单")
                    session.finish()
            elif stripped_arg == "ok":
                session.finish()
            else:
                session.state['message'] = stripped_arg
        return

    if stripped_arg:
        #这里进行学习和其他操作
        # 这里就图片处理
        if 'image' in stripped_arg or 'bface' in stripped_arg:
            if 'bface' in stripped_arg:
                file=stripped_arg
            else:
                file = download(stripped_arg[stripped_arg.find("url=") + 4:-1])
                file = "[CQ:image,file=face/" + file + "]"
            # 先找关键词
            sql="SELECT temp FROM chat WHERE QQ='"+str(QQ)+"'"
            result=sql_dql(sql)
            file=result[0][0]+"-"+file
            if addreplay(file):
                await session.send("[CQ:at,qq=" + str(QQ) + "]添加图片回复成功")
            else:
                await session.send("[CQ:at,qq=" + str(QQ) + "]添加失败！")
            session.finish()
        elif "-" in stripped_arg:
            if addreplay(stripped_arg):
                await session.pause("[CQ:at,qq=" + str(QQ) + "]添加成功，继续输入可继续学习，输入“退出”即可退出学习模式")
            else:
                await session.send("[CQ:at,qq=" + str(QQ) + "]添加失败，已退出学习模式")
                session.finish()
        elif stripped_arg.isdigit():
            value=int(stripped_arg)
            if value<50:
                #这里说明是编辑关键词
                sql="SELECT temp FROM chat WHERE QQ='"+str(QQ)+"'"
                result=sql_dql(sql)
                if result:
                    result=result[0][0].split("-")
                    result=result[int(stripped_arg)]
                    # 删除关键词
                    sql="DELETE FROM cKeyword WHERE thekey='"+result+"'"
                    if sql_dml(sql):
                        await session.send("[CQ:at,qq=" + str(QQ) + "]成功删除关键词:"+result)
                    else:
                        await session.send("[CQ:at,qq=" + str(QQ) + "]删除关键词("+result+")失败")
                    session.finish()
            else:
                sql = "INSERT INTO believe (QQ) VALUES ('" + stripped_arg + "')"
                if sql_dml(sql):
                    await session.send("[CQ:at,qq=" + str(QQ) + "]添加成功!")
                    session.finish()
                else:
                    await session.send("[CQ:at,qq=" + str(QQ) + "]添加失败，该用户已存在")
                    session.finish()
        # 退出学习模式
        elif stripped_arg == "退出":
            await session.send("已退出学习模式")
            session.finish()
        else:
            await session.send("错误回复,已退出")
            session.finish()

    # session.finish()
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg
#这里是添加语音回复的代码

#下载图片代码
def download(url):
    try:
        req = requests.get(url, timeout=5)
        t = time.time()
        filename=str(int(t))+".jpg"
        with open('data/image/face/'+filename, 'wb') as code:
            code.write(req.content)
        return filename
    except Exception:
        return None


# 这里用函数来添加回复
def addreplay(content):
    data = content.split("-")
    # 内容不能为空
    if not data[0] or not data[1]:
        return False
    # 这里提取一下优先级
    weight=50
    if len(data)==3:
        weight=data[2]
    # 先找找关键词是否存在
    sql = "SELECT thekey,replay FROM cKeyword WHERE thekey='" + data[0] + "'"
    dta = sql_dql(sql)
    if dta:
        # 关键词存在
        sql = "UPDATE cKeyword SET replay='" + dta[0][1] + data[1] + "@@',weight="+str(weight)+" WHERE thekey='" + data[0] + "'"
    else:
        sql = "INSERT INTO cKeyword (thekey,replay,weight) VALUES ('" + data[0] + "','" + data[1] + "@@',"+str(weight)+")"
    return sql_dml(sql)


# 特定关键词回复
@on_natural_language
async def _(session: NLPSession):
    # 这里会保留所有的会话消息

    message = session.msg.strip()
    # 先把所有的数据都读出来
    sql = "SELECT keyword,replay FROM keyword WHERE keyword='" + message + "'"
    result = sql_dql(sql)
    if result:
        replay = result[0][1].split("@@")
        content = replay[random.randint(0, len(replay) - 2)]
    else:
        return None
    return IntentCommand(95.0, 'keyword', args={'message': content})


# 包含关键词回复
@on_natural_language
async def _(session: NLPSession):
    # 这里会保留所有的会话消息
    QQ = session.ctx['user_id']
    message = session.msg.strip()
    # 先把所有的数据都读出来
    sql = "SELECT thekey,replay,reWeight,weight FROM cKeyword WHERE '" + message + "' LIKE CONCAT('%',thekey,'%')"
    result = sql_dql(sql)
    #这里是优先级的设置
    priority=70
    # content=result[0][1]
    if result:
        # 我们这里匹配最长的
        klen = 0
        weight=0
        strg = ""
        for data in result:
            tlen = len(data[0])
            #如果完全匹配
            if data[0].strip()==message:
                priority=95
                strg=data[1]
                break
            if tlen > klen or data[3]>weight:
                klen = tlen
                weight=data[3]
                message=data[0]
                strg = data[1]
                priority=int(data[2])
        replay = strg.split("@@")
        content = replay[random.randint(0, len(replay) - 2)]
        # 这里负责关键词的删除
        sql="UPDATE chat SET keyDelete='"+message+"-"+content+"' WHERE QQ='"+str(QQ)+"'"
        sql_dml(sql)
    else:
        return None
    return IntentCommand(priority, 'keyword', args={'message': content})


# 进入学习功能
@on_natural_language(keywords={'学习', '信任', '？', '#','编辑','删除该回复'})
async def _(session: NLPSession):
    QQ = session.ctx['user_id']
    # 去掉消息首尾的空白符
    key_list = ['学习模式', '学习']
    # 添加信任人员
    add_list = ['添加信任', '信任']
    stripped_msg = session.msg.strip()
    data = ""
    # 对消息进行分词和词性标注
    for key in key_list:
        if key == stripped_msg:
            data = "学习"
    for key in add_list:
        if key == stripped_msg:
            data = "信任"
    if stripped_msg.startswith('#') or stripped_msg=='删除该回复':
        data = stripped_msg

    # 快捷添加
    if stripped_msg.startswith("？") and "-" in stripped_msg:
        sql = "SELECT QQ FROM believe WHERE QQ='" + str(QQ) + "'"
        if sql_dql(sql):
            if addreplay(stripped_msg[1:]):
                await session.send("[CQ:at,qq=" + str(QQ) + "]添加成功！")
            else:
                await session.send("[CQ:at,qq=" + str(QQ) + "]添加失败")
        else:
            await session.send("[CQ:at,qq=" + str(QQ) + "]抱歉，你不在信任名单")
        data = "ok"
    #编辑关键词
    if stripped_msg.startswith("编辑关键词"):
        # 添加操作
        sql = "UPDATE chat SET theoption='关键词' WHERE QQ='" + str(QQ) + "'"
        if sql_dml(sql):
            data=stripped_msg
        else:
            data="ok"

    if data == "":
        return None
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'keyword', current_arg=data or '')

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
    # print(data)
    return data


# 把数据库的操作函数都封装到一个函数里面，避免麻烦
def sql_dql(sql):
    data = getconfig()
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"],
                         db=data["db"], charset='utf8')
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
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"],
                         db=data["db"], charset='utf8')
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

import asyncio
from typing import Callable
import MySQLdb,time
import configparser
from aiocqhttp.message import *
from .helpers import send

from . import NoneBot
from .command import handle_command, SwitchException
from .log import logger
from .natural_language import handle_natural_language
from .typing import Context_T

_message_preprocessors = set()


def message_preprocessor(func: Callable) -> Callable:
    _message_preprocessors.add(func)
    return func


async def handle_message(bot: NoneBot, ctx: Context_T) -> None:
    _log_message(ctx)

    if not ctx['message']:
        ctx['message'].append(MessageSegment.text(''))
    #更新状态
    try :
        text = str(ctx['message'])
        QQ = ctx['user_id']
        messageid=ctx['message_id']
        groupid=ctx['group_id']
        last=0
        #把数据插进去(统计群聊信息)
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql="INSERT INTO message (QQ,message,time,groupid) VALUES ("+str(QQ)+",'"+text+"','"+t+"',"+str(groupid)+")"
        sql_dml(sql)
        # 判断主人的状态
        data=getconfig()
        if '[CQ:at,qq='+data['qq']+']' in text:
            sql="SELECT thevalue FROM options WHERE id=1"
            result=sql_dql(sql)
            if result[0][0]:
                await send(bot, ctx, '[CQ:at,qq=' + str(QQ) + ']'+result[0][0])
        sql="SELECT messageid FROM chat WHERE QQ='"+str(QQ)+"'"
        result=sql_dql(sql)
        if result:
            last=result[0][0]
        sql1="INSERT INTO chat(QQ,lastchat,messageid,lmessageid) VALUES('"+str(QQ)+"','"+text+"',"+str(messageid)+","+str(last)+")"
        sql2="UPDATE chat SET lastchat='"+text+"',messageid="+str(messageid)+",lmessageid="+str(last)+" WHERE QQ='"+str(QQ)+"'"
        if not sql_dml(sql1):
            sql_dml(sql2)
        # if '小游君' in ctx['message']:
        sql = "SELECT text,describetion FROM sensitiveWord WHERE '" + text + "' LIKE CONCAT('%',text,'%')"
        result=sql_dql(sql)
        if result:
            des = result[0][1]
            # 判断还有几次机会
            sql="SELECT chance FROM chat WHERE QQ='"+str(QQ)+"'"
            result=sql_dql(sql)
            chance = result[0][0]
            # group_id	number	-	群号
            # user_id	number	-	要禁言的 QQ 号
            # duration
            say=['屡教不改，给你一天时间让你反省自己的言行','之前怎和你说的？最后一次机会了，好好珍惜','看在你初犯的份上，你还有两次机会']
            if chance==1:
                #禁言
                try:
                    await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=60 * 60 * 24)
                except:
                    pass
            chance-=1
            try:
               await bot.delete_msg(message_id=ctx['message_id'])
            except:
                pass
            await send(bot,ctx,'[CQ:at,qq='+str(QQ)+']'+des+say[chance])
            if chance==0:
                chance=3
            sql="UPDATE chat SET chance="+str(chance)+" WHERE QQ='"+str(QQ)+"'"
            sql_dml(sql)
            return
    except:
        pass
    coros = []
    for processor in _message_preprocessors:
        coros.append(processor(bot, ctx))
    if coros:
        await asyncio.wait(coros)

    raw_to_me = ctx.get('to_me', False)
    _check_at_me(bot, ctx)
    _check_calling_me_nickname(bot, ctx)
    ctx['to_me'] = raw_to_me or ctx['to_me']

    while True:
        try:
            handled = await handle_command(bot, ctx)
            break
        except SwitchException as e:
            # we are sure that there is no session existing now
            ctx['message'] = e.new_ctx_message
            ctx['to_me'] = True
    if handled:
        logger.info(f'Message {ctx["message_id"]} is handled as a command')
        return

    handled = await handle_natural_language(bot, ctx)
    if handled:
        logger.info(f'Message {ctx["message_id"]} is handled '
                    f'as natural language')
        return


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



# 这里加上数据库的操作函数
# 把数据库的操作函数都封装到一个函数里面，避免麻烦
def sql_dql(sql):
    data=getconfig()
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
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"], db=data["db"],charset='utf8')
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


def _check_at_me(bot: NoneBot, ctx: Context_T) -> None:
    if ctx['message_type'] == 'private':
        ctx['to_me'] = True
    else:
        # group or discuss
        ctx['to_me'] = False
        at_me_seg = MessageSegment.at(ctx['self_id'])

        # check the first segment
        first_msg_seg = ctx['message'][0]
        if first_msg_seg == at_me_seg:
            ctx['to_me'] = True
            del ctx['message'][0]

        if not ctx['to_me']:
            # check the last segment
            i = -1
            last_msg_seg = ctx['message'][i]
            if last_msg_seg.type == 'text' and \
                    not last_msg_seg.data['text'].strip() and \
                    len(ctx['message']) >= 2:
                i -= 1
                last_msg_seg = ctx['message'][i]

            if last_msg_seg == at_me_seg:
                ctx['to_me'] = True
                del ctx['message'][i:]

        if not ctx['message']:
            ctx['message'].append(MessageSegment.text(''))


def _check_calling_me_nickname(bot: NoneBot, ctx: Context_T) -> None:
    first_msg_seg = ctx['message'][0]
    if first_msg_seg.type != 'text':
        return

    first_text = first_msg_seg.data['text']

    if bot.config.NICKNAME:
        # check if the user is calling me with my nickname
        if isinstance(bot.config.NICKNAME, str) or \
                not isinstance(bot.config.NICKNAME, Iterable):
            nicknames = (bot.config.NICKNAME,)
        else:
            nicknames = filter(lambda n: n, bot.config.NICKNAME)
        nickname_regex = '|'.join(nicknames)
        m = re.search(rf'^({nickname_regex})([\s,，]*|$)',
                      first_text, re.IGNORECASE)
        if m:
            nickname = m.group(1)
            logger.debug(f'User is calling me {nickname}')
            ctx['to_me'] = True
            first_msg_seg.data['text'] = first_text[m.end():]


def _log_message(ctx: Context_T) -> None:
    msg_from = str(ctx['user_id'])
    if ctx['message_type'] == 'group':
        msg_from += f'@[群:{ctx["group_id"]}]'
    elif ctx['message_type'] == 'discuss':
        msg_from += f'@[讨论组:{ctx["discuss_id"]}]'
    logger.info(f'Self: {ctx["self_id"]}, '
                f'Message {ctx["message_id"]} from {msg_from}: '
                f'{ctx["message"]}')

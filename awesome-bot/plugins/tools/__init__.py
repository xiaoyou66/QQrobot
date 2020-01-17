from jieba import posseg
import MySQLdb

import sys,configparser
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

@on_command('tools', aliases=('状态','工具')) #这里是命令的几个关键词
async def tools(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    #获取用户的QQ号
    QQ=session.ctx['user_id']
    #如果没有获取到城市数据，那么就会中断这个函数
    message= session.get('message')
    if message!='ok':
        data=getconfig()
        if QQ==int(data['qq']):
            if message=='我有空':
                row=''
            else:
                row=message
            sql="UPDATE options SET thevalue='"+row+"' WHERE id=1"
            if sql_dml(sql):
                await session.send("更新状态成功！")
            else:
                await session.send("更新状态失败！")
    # # 向用户发送天气预报
    # await session.send(weather_report)

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@tools.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            if stripped_arg=='ok':
                session.finish()
                return
            else:
                session.state['message'] = stripped_arg

        return


    # # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg


# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'撤回','状态'})
async def _(session: NLPSession):
    QQ = session.ctx['user_id']
    # 去掉消息首尾的空白符
    message = session.msg.strip()
    content=""
    # 下面是常见命令
    back_list=['撤回我刚才的内容','快撤回','撤回','撤回我说的']
    #下面是命令判断
    if message in back_list:
        sql="SELECT lmessageid FROM chat WHERE QQ='"+str(QQ)+"'"
        result=sql_dql(sql)
        bot=session.bot
        try:
            await bot.delete_msg(message_id=result[0][0])
            await session.send('撤回成功！')
        except:
            await session.send('撤回失败！')
            content='ok'
    elif message.startswith("状态"):
        if QQ==1487998424:
            row=message[2:]
            sql="UPDATE options SET thevalue='"+row+"' WHERE id=1"
            if sql_dml(sql):
                await session.send("更新状态成功！")
            else:
                await session.send("更新状态失败！")
            content = 'ok'
        else:
            return None
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'tools', current_arg=content or '')


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
    # print(data)
    return data


# 把数据库的操作函数都封装到一个函数里面，避免麻烦
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

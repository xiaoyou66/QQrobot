from os import path
import random
import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand


def 洗牌遍历(列表,重复度):
    池 = list(列表) * 重复度
    while True:
        random.shuffle(池)
        for 元素 in 池:
            yield 元素


def 来点名人名言(前面垫话,后面垫话,下一句名人名言):
    xx = next(下一句名人名言)
    xx = xx.replace(  "a",random.choice(前面垫话) )
    xx = xx.replace(  "b",random.choice(后面垫话) )
    return xx

def 另起一段():
    xx = ". "
    xx += "\r\n"
    xx += "    "
    return xx

@on_command('sign', aliases=('狗屁不通文章')) #这里是命令的几个关键词
async def sign(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    QQ=session.ctx['user_id']
    #如果没有获取到城市数据，那么就会中断这个函数
    content= session.get('title', prompt='[CQ:at,qq='+str(QQ)+']请输入生成文章的主题')
    return

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@sign.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
            # 该命令第一次运行（第一次进入命令会话）
            QQ = session.ctx['user_id']
            # 如果没有获取到城市数据，那么就会中断这个函数
            session.pause('[CQ:at,qq=' + str(QQ) + ']请输入生成文章的主题')
            return
    # 这里直接生成文章

    if stripped_arg:
        # await session.send(stripped_arg)
        filepath = path.dirname(__file__) + "/data.json"
        data = readJSON.读JSON文件(filepath)
        名人名言 = data["famous"]  # a 代表前面垫话，b代表后面垫话
        前面垫话 = data["before"]  # 在名人名言前面弄点废话
        后面垫话 = data['after']  # 在名人名言后面弄点废话
        废话 = data['bosh']  # 代表文章主要废话来源
        xx = stripped_arg
        重复度 = 2
        下一句废话 = 洗牌遍历(废话,重复度)
        下一句名人名言 = 洗牌遍历(名人名言,重复度)
        tmp = str()
        while (len(tmp) < 3000):
            分支 = random.randint(0, 100)
            if 分支 < 5:
                tmp += 另起一段()
            elif 分支 < 20:
                tmp += 来点名人名言(前面垫话,后面垫话,下一句名人名言)
            else:
                tmp += next(下一句废话)
        tmp = tmp.replace("x", xx)
        await session.send(tmp)
        # print(content)
        # 向用户发送天气预报
        # await session.send("正在生成！"+content)
        # await session.send(str(content))
    session.finish()
    # if not stripped_arg:
    #     # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
    #     QQ=session.ctx['user_id']
    #     # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
    #     session.pause('[CQ:at,qq='+str(QQ)+']输入错误')
    #
    # # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg


# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'狗屁不通文章'})
async def _(session: NLPSession):

    # 直接发送空命令，要用户自己输入主题
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'sign', current_arg='文章')
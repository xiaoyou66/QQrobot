from .data_source import get_weather_of_city,get_weather_of_city_time
from jieba import posseg

import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

@on_command('weather', aliases=('天气', '天气预报', '查天气')) #这里是命令的几个关键词
async def weather(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    #获取用户的QQ号
    QQ=session.ctx['user_id']
    #如果没有获取到城市数据，那么就会中断这个函数
    content= session.get('city', prompt='[CQ:at,qq='+str(QQ)+']你想查询哪个城市的天气呢？')
    #判断得的是字符串还是字典，然后执行不同
    if isinstance(content,dict):
        weather_report = await get_weather_of_city_time(content)
    else:
        weather_report = await get_weather_of_city(content)
    # 向用户发送天气预报
    await session.send(weather_report)

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@weather.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['city'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        QQ=session.ctx['user_id']
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('[CQ:at,qq='+str(QQ)+']要查询的城市名称不能为空呢，请重新输入')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg


# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'天气'})
async def _(session: NLPSession):
    # 去掉消息首尾的空白符
    stripped_msg = session.msg_text.strip()
    # 对消息进行分词和词性标注
    words = posseg.lcut(stripped_msg)

    #设置城市还有时间
    content={}
    # 遍历 posseg.lcut 返回的列表
    for word in words:
        # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
        if word.flag == 'ns':
            # ns 词性表示地名
            content['city']= word.word
        if word.flag=='t':
            #t是时间词
            content['time']=word.word
    # 如果没有找到城市就直接忽略
    if 'city' not in content:
        return None
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'weather', current_arg=content or '')
from jieba import posseg
from .sendData import speakvoice
from .sendData import Getbackground

import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

@on_command('voice', aliases=('语音','语音合成')) #这里是命令的几个关键词
async def voice(session: CommandSession):
    # 获取到关键词的内容
    key = session.get('key', prompt='')
    await session.send("(语音)关键词:"+key)
    if key:
        result=await speakvoice(key)
        await session.send(result)
    else:
        await session.send("没有提取到关键词！")

''
@voice.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['key'] = stripped_arg
        return


# 这里是语音接口
@on_natural_language(keywords={'说','读','语音'})
async def _(session: NLPSession):
    # 去掉消息首尾的空白符
    row = session.msg_text
    # 语音的一些很简单的关键词
    key_start=['读一下','说一下','发语音','说','读','语音','快说']
    key_end=['怎么读','怎么说']
    key=""
    # 判断关键词的开头
    for tkey in key_start:
        if row.startswith(tkey):
            key=row[row.find(tkey)+len(tkey):]
            break
    if not key:
        # 判断关键词的结尾
        for tkey in key_end:
            if row.endswith(tkey):
                key=row[:row.find(tkey)]
                break
    
    if not key:
        return None

    # 对消息进行分词和词性标注
    # words = posseg.lcut(row)

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'voice', current_arg=key or '')



# 下面这个些是用来处理背景音乐
####################################

@on_command('background', aliases=('音效','效果')) #这里是命令的几个关键词
async def background(session: CommandSession):
    # 获取到关键词的内容
    key = session.get('key', prompt='')
    await session.send("（音效）关键词:"+key)
    if key:
        result=await Getbackground(key)
        await session.send(result)
    else:
        await session.send("没有提取到关键词！")



@background.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['key'] = stripped_arg
        return


# 这里是音效接口
@on_natural_language(keywords={'听','叫','音效','声','音','效果','来个','来一个'})
async def _(session: NLPSession):
    # 去掉消息首尾的空白符
    row = session.msg_text.strip()
    key=""
    # 这里处理一下音乐和音效之间的冲突
    music_start=['我要听','我想听','来一个','来个']
    music_end=['叫','声','音效','效果']
    flag=0
    for tkey in music_start:
        for ekey in music_end:
            if row.startswith(tkey):
                if row.endswith(ekey):
                    key = row.replace(tkey, "")
                flag=1
    #处理不到数据就叫给音乐来处理
    if (not key) and flag:
        return None
    #这里处理形如猪叫的句子(需要加后缀的)
    if not key:
        key_end=['怎么叫']
        for tkey in key_end:
            if row.endswith(tkey):
                key=row[:row.find(tkey)]+"叫"
    #这里则直接处理声音效等问题
    if not key:
        key_end=['声','音效','音','声音','叫']
        for tkey in key_end:
            if row.endswith(tkey):
                key=row

    if not key:
        return None

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(85.0, 'background', current_arg=key or '')






import random
import sys
sys.path.append('.../')
from nonebot import on_request, RequestSession,on_notice, NoticeSession

# 机器人自动同意加群申请
@on_request('group') #把函数注册为请求处理器
async def _(session: RequestSession):
     #这里直接同意加群请求
    await session.approve()
    return

# 将函数注册为群成员增加通知处理器
@on_notice('group_increase')
async def _(session: NoticeSession):
    QQ=session.ctx['user_id']
    #欢迎词列表
    welcome=['叮咚，你已经进入了次元世界，这里有来自不同星球的生物/人类','要要要~切克闹，欢迎你的来到。','文明关流，大家热闹，禁止发广告。','今天天气不错，欢迎新人来到。','你匿了那么久，现在终于入群了。','欢迎新人，么么哒！','欢迎欢迎！','哎呦你终于来了','举朵小花欢迎你！']
    notice="\n[CQ:face,id=176]有关主题问题可以先看帮助文档(http://help.xiaoyou66.com),实在不会再到群里问。\n[CQ:face,id=212]不要发广告，不要发暴力色情图片，发了直接踢群\n[CQ:face,id=21]本群什么话题都可以讨论(政治敏感话题除外)，欢迎各种水群！"
    ran=random.randint(0,len(welcome)-1)
    # 发送欢迎消息
    await session.send('[CQ:at,qq='+str(QQ)+']'+welcome[ran]+notice)
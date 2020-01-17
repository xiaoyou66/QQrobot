from jieba import posseg
from .music import getmusic
from os import path
import MySQLdb
import json
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests,configparser
import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand


@on_command('music', aliases=('点歌'))  # 这里是命令的几个关键词
async def music(session: CommandSession):
    # 获取用户的QQ号
    QQ = session.ctx['user_id']
    content = session.get('music')
    await session.send("关键词:" + content['key'] + " 音乐源:" + content['type'])
    if content['key']:
        music = await getmusic(content)
        id = music['id']
        name=music['name']
        sigr=music['singr']
        mtype=music['type']
        sigr=sigr.strip()
        sigr=sigr.replace(" ",",")
        # 把内容写到文本里面
        with open(path.dirname(__file__)+'\\nowmusic.txt','w',encoding='UTF-8') as f:
            f.write(str(id)+" "+mtype+" "+name+" "+sigr)
        rowjson = json.dumps(music, ensure_ascii=False)
        # 转义字符替换
        rowjson = rowjson.replace("'", "\\\'")
        sql = "UPDATE music SET list='" + rowjson + "' WHERE QQ='" + str(QQ) + "'"
        if not sql_dml(sql):
            await session.send("插入数据库失败")
        await session.send("[CQ:music,type=" + content['type'] + ",id=" + str(id) + "]")
    else:
        await session.send("[CQ:face,id=174]没有找到关键词，换一个说法试试！")


# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@music.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    QQ = session.ctx['user_id']
    if session.is_first_run:
        sql = "SELECT type FROM music WHERE QQ=" + str(QQ)
        # 首先判断用户有没有设置音乐来源
        content = sql_dql(sql)
        #我的收藏和收藏很容易搞混，所以就单独加一个数组
        likelist=['我的收藏','我收藏的音乐','我喜欢的歌','我喜欢的音乐']
        #编辑收藏夹同样很容易和其他的搞混，这里也加一个数组
        editlist=['编辑收藏夹','修改收藏夹','清空收藏夹','编辑收藏','修改收藏']
        # 这里是用户的一些其他的操作
        if "源" in stripped_arg and content:
            sql = "UPDATE chat SET theoption='源' WHERE QQ='" + str(QQ) + "'"
            sql_dml(sql)
            session.pause("请回复下面内容即可更换音乐源:\n回复\"1\"为网易云音乐\n回复\"2\"为QQ音乐")
        elif not content:
            # 自己手动更换音乐源
            sql = "INSERT INTO music(QQ,type) VALUES ('" + str(QQ) + "','qq')"
            sql_dml(sql)
            stripped_arg['type'] = 'qq'
            session.state['music'] = stripped_arg
            # 这里是最后的情况，这里直接返回一个字典
            # 这里显示播放列表
        elif '表' in stripped_arg:
            data = musiclist(QQ, 0)
            if data:
                await session.pause(data)
            else:
                await session.send("没有播放列表！")
                session.finish()
        elif '一首' in stripped_arg:
            # 这里为了简化代码，所以直接使用一个函数
            await session.send(changemusic(stripped_arg, QQ))
            session.finish()
        # 这里处理编辑收藏夹的情况
        elif stripped_arg in editlist:
            data=musiclist(QQ,2)
            if data:
                await session.pause(data)
            else:
                await session.send("没有收藏！")
        # 这里负责处理我的收藏
        elif stripped_arg in likelist:
            data=musiclist(QQ,1)
            if data:
                await session.pause(data)
            else:
                await session.send("没有收藏！")
                session.finish()
        #这里负责生成词云功能
        elif '词云' in stripped_arg:
            await session.send("该功能需要爬取1000条评论，同时还需要生成词云，持续时间较久(大概15秒)，请耐心等待[CQ:face,id=174]")
            await session.send(cloudyun())
            session.finish()
        elif '藏' in stripped_arg or '喜欢' in stripped_arg:
            await session.send(like(QQ))
            session.finish()
        elif stripped_arg and (stripped_arg is not str):
            stripped_arg['type'] = content[0][0]
            session.state['music'] = stripped_arg
        return

    # 这里就是判断一下用户的选择（这里主要用于更换音乐源）
    sql = "SELECT lastchat,theoption FROM chat WHERE QQ='" + str(QQ) + "'"
    content = sql_dql(sql)
    if content:
        # 这里判断一下选择的是第几首歌
        if content[0][1] == "列表" or content[0][1]=="收藏":
            if not stripped_arg.isdigit():
                await session.send("你输入有误，已忽略")
                session.finish()
                return None
            num = int(stripped_arg)
            # 先获取到json数据
            sql = "SELECT list,likelist FROM music WHERE QQ='" + str(QQ) + "'"
            data = sql_dql(sql)
            if data:
                # 获取到我们需要的json数据
                if content[0][1]=="收藏":
                    musics=data[0][1]
                    musics=json.loads(musics)
                    if num<=len(musics):
                        id=musics[num-1]['id']
                        type=musics[num-1]['type']
                        await session.send("[CQ:music,type=" + type + ",id=" + str(id) + "]")
                    else:
                        await session.send("没有找到这首歌，已忽略")
                else:
                    musics = data[0][0]
                    # 这里我们解析json数据
                    musics = json.loads(musics)
                    if num<=len(musics['result']):
                        nowid = musics['result'][num - 1]['id']
                        musics['id'] = nowid
                        await session.send("[CQ:music,type=" + musics['type'] + ",id=" + str(nowid) + "]")
                        rowjson = json.dumps(musics, ensure_ascii=False)
                        rowjson = rowjson.replace("'", "\\\'")
                        sql = "UPDATE music SET list='" + rowjson + "' WHERE QQ='" + str(QQ) + "'"
                        sql_dml(sql)
                    else:
                        await session.send("没有找到这首歌，已忽略")
                session.finish()
                return
            else:
                await session.send("数据库错误！")
                session.finish()
                return
        #这里是修改收藏夹
        elif content[0][1]=='编辑':
            try:
                lists=stripped_arg.split(" ")
                # #先把数据都读出来
                sql = "SELECT likelist FROM music WHERE QQ='" + str(QQ) + "'"
                data = sql_dql(sql)
                if data:
                    musics = data[0][0]
                    musics = json.loads(musics)
                    newmusics=[]
                    for i in range(1,len(musics)+1):
                        if str(i) not in lists:
                            newmusics.append(musics[i-1])
                    rowjson = json.dumps(newmusics, ensure_ascii=False)
                    rowjson = rowjson.replace("'", "\\\'")
                    sql = "UPDATE music SET likelist='" + rowjson + "' WHERE QQ='" + str(QQ) + "'"
                    if sql_dml(sql):
                        await session.send("[CQ:face,id=13]编辑收藏夹成功！")
                    else:
                        await session.send("收藏失败！")
            except:
                await session.send("删除时出现异常，已忽略此次会话")
            session.finish()
            return

        # 获取用户上一步输入，然后进行切换
        if stripped_arg == '1':
            type = "163"
            name = "网易云"
        elif stripped_arg == '2':
            type = "qq"
            name = "QQ"
        else:
            await session.send("输入错误，已忽略")
            session.finish()
            return
        if '源' in content[0][1] and content:
            # 这里执行一下命令
            sql= "UPDATE music SET type='" + type + "' WHERE QQ='" + str(QQ) + "'"
            if sql_dml(sql):
                await session.send("[CQ:face,id=101]你已成功选择了" +name+ "音乐作为播放源，可以开始你的音乐之旅了！\n小提示:输入\"更换音乐源\"即可更换！")
            else:
                await session.send("未知错误！")
    # 结束当前会话
    session.finish()

def cut(comment):
    stop_words=['音乐','一条','首歌']
    word_pairs = posseg.lcut(comment, HMM=False)
    result = []
    for t in word_pairs:
        if not t.word in stop_words:
            result.append(t.word)
    return '/'.join(result)


#这个是生成词云的函数
def cloudyun():
    try:
        # 先读取TXT文本
        with open(path.dirname(__file__) + '\\nowmusic.txt', 'r', encoding='UTF-8') as f:
            musicdetail = f.read()
        musicdetail = musicdetail.split(" ")
        type=musicdetail[1]
        id=musicdetail[0]
        if type!="163":
            return "当前仅支持网易云音乐"
        limit = 20
        offset = 0
        # 这里直接爬2000条评论
        text = ""
        while True:
            url = "http://music.163.com/api/v1/resource/comments/R_SO_4_"+str(id)
            params = {
                'limit': limit,
                'offset': offset,
            }
            head = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
            }
            offset += 20
            resopnse = requests.get(url, params=params, headers=head).text
            datas = json.loads(resopnse)
            for data in datas['comments']:
                text += cut(data['content'])
            if offset == 1000:
                break
        font = 'microsoft-yahei.ttf'
        wc = WordCloud(max_words=500, background_color="white", collocations=False, font_path=font, width=1400, height=1400,
                       margin=2).generate(text.lower())
        plt.imshow(wc)
        plt.axis("off")
       # plt.show()
        filepath = "data/image/myimage/"
        wc.to_file(filepath+'1.png')  # 把词云保存下来
        return "[CQ:image,file=myimage/1.png]"
    except:
        return "生成失败！"

# 这里是查看播放列表
def musiclist(QQ, optoion):
    # 这里执行一下添加操作的命令
    if optoion==0:
        # 0是列表，1是收藏 2是编辑收藏夹
        sql = "UPDATE chat SET theoption='列表' WHERE QQ='" + str(QQ) + "'"
    elif optoion==1:
        sql = "UPDATE chat SET theoption='收藏' WHERE QQ='" + str(QQ) + "'"
    elif optoion==2:
        sql = "UPDATE chat SET theoption='编辑' WHERE QQ='" + str(QQ) + "'"
    sql_dml(sql)
    # 先获取到json数据
    sql = "SELECT list,likelist	 FROM music WHERE QQ='" + str(QQ) + "'"
    data = sql_dql(sql)
    if data:
        if optoion==0:
            # 获取到我们需要的json数据
            musics = data[0][0]
            # 这里我们解析json数据
            musics = json.loads(musics)
            nowid = musics['id']
            musics = musics['result']
            senddata = ""
            for i in range(1, len(musics) + 1):
                senddata += str(i) + "." + musics[i - 1]['name'] + "-" + musics[i - 1]['sginer'] + "\n"
                if musics[i - 1]['id'] == nowid:
                    nowid = i
            senddata = "当前为第" + str(nowid) + "首歌\n[CQ:face,id=140]----播放列表----[CQ:face,id=144]\n" + senddata + "------------\n小提示:回复对应数字即可播放当前歌曲"
            return senddata
        else:
            musics=data[0][1]
            if musics:
                musics = json.loads(musics)
                senddata = ""
                for i in range(0,len(musics)):
                    senddata+=str(i+1)+"."+musics[i]['name']+"-"+musics[i]['sginer']+"\n"
                if optoion == 1:
                    senddata="[CQ:face,id=66]--我的收藏--[CQ:face,id=66]\n"+senddata+"----------------\n小提示:回复对应数字即可播放当前歌曲\n收藏歌曲不支持上一首，下一首切换哦"
                else:
                    senddata="[CQ:face,id=66]--我的收藏--[CQ:face,id=66]\n"+senddata+"----------------\n小提示:回复对应数字即可删除该歌曲\n如果需要删除多个请用空格把它们隔开"
                return senddata
            else:
                return ""
    else:
        return ""


# 处理喜欢这首歌的问题
def like(QQ):
    # 先获取到json数据
    sql = "SELECT list,likelist FROM music WHERE QQ='" + str(QQ) + "'"
    data = sql_dql(sql)
    like = {}
    if data:
        musicdetail=""
        with open(path.dirname(__file__) + '\\nowmusic.txt', 'r', encoding='UTF-8') as f:
            musicdetail=f.read()
        musicdetail=musicdetail.split(" ")
        like['name'] = musicdetail[2]
        like['sginer'] = musicdetail[3]
        like['id'] = musicdetail[0]
        like['type'] = musicdetail[1]
         # 先获取到歌单
        likes = data[0][1]
        # 不能让id重复
        # 不为空就想办法加到列表里面
        if likes:
            likes = json.loads(likes)
            for i in likes:
                if i['id'] == like['id']:
                    return "你已经收藏过该歌曲了，请勿重复收藏！"
            likes.append(like)
            likes = json.dumps(likes, ensure_ascii=False)
        else:
            llike = [""]
            llike[0] = like
            likes = json.dumps(llike, ensure_ascii=False)
        # 保存数据
        likes = likes.replace("'", "\\\'")
        sql = "UPDATE music SET likelist='" + likes + "' WHERE QQ='" + str(QQ) + "'"
        if sql_dml(sql):
            return "[CQ:face,id=175]收藏成功!\n小提示：输入我的收藏即可查看你收藏的音乐哦！"
        else:
            return "收藏失败！"


# 处理上一首，下一首，换一首的问题
def changemusic(key, QQ):
    # 先获取到json数据
    sql = "SELECT list FROM music WHERE QQ='" + str(QQ) + "'"
    data = sql_dql(sql)
    if data:
        # 获取到我们需要的json数据
        musics = data[0][0]
        # 这里我们解析json数据
        musics = json.loads(musics)
        musiclist = musics['result']
        # 把所有的id加到列表里面
        idlist = []
        nowid = 0
        for i in range(0, len(musiclist)):
            if musiclist[i]['id'] == musics['id']:
                nowid = i
            idlist.append(musiclist[i])
        # 这里开始判断类型
        if key == "上一首":
            if nowid - 1 < 0:
                nowid = 10
            else:
                nowid -= 1
        elif key == "下一首":
            if nowid + 1 > 9:
                nowid = 1
            else:
                nowid += 1
        elif key == "换一首":
            nowid = random.randint(0, 9)
    else:
        return "播放列表为空！"
    musics['id'] = musics['result'][nowid]['id']
    rowjson = json.dumps(musics, ensure_ascii=False)
    rowjson = rowjson.replace("'", "\\\'")
    sql = "UPDATE music SET list='" + rowjson + "' WHERE QQ='" + str(QQ) + "'"
    sql_dml(sql)
    return "[CQ:music,type=" + musics['type'] + ",id=" + str(musics['id']) + "]"


key_list = ['听', '歌']

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
    db = MySQLdb.connect(host=data["ip"], port=int(data["port"]), user=data["user"], password=data["passwd"], db=data["db"], charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        db.close()
        return 1
    except Exception:
        db.rollback()
        db.close()
        return Exception

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




# 这里主要用于执行命令
@on_natural_language(keywords={'源', '表', '首', '藏', '喜欢','词云'})
async def _(session: NLPSession):
    # 这些是关键词
    key_list = ['更换音乐源', '切换音乐源', '我要更换音乐源', '我想更换音乐源','换源', '播放列表',  '当前播放列表', '换一首', '下一首', '上一首', '收藏这首歌', '喜欢这首歌',
                '收藏','收藏这个','我喜欢这首歌','我的收藏','我收藏的音乐','我喜欢的歌','我喜欢的音乐','编辑收藏夹','修改收藏夹','清空收藏夹','编辑收藏','修改收藏','生成词云','词云']
    row = session.msg_text.strip()
    if row in key_list:
        return IntentCommand(90.0, 'music', current_arg=row or '')
    else:
        return None


# 这里用于获取音乐的名字
@on_natural_language(keywords={'首', '听', '歌', '歌词'})
async def _(session: NLPSession):
    QQ = session.ctx['user_id']
    row = session.msg_text.strip()
    # 对消息进行分词和词性标注
    words = posseg.lcut(row)

    # 歌的量词
    music_cout = ['歌曲','来个','放首', '来首', '来一首','点歌']

    # 一些关键词，主要用于过滤
    keyword = ""
    # 这里来解析一下
    method = 0
    for i in range(len(words)):
        # 听前面一般是东西
        if words[i].word == '听' and (words[i - 1].flag == 'v' or i == 0):
            method = 1

    # 判断来首的情况
    if method == 0:
        for word in music_cout:
            # 判断 是否有关键词
            if word in row:
                # 这里简单的判断一下，关键词应该在前面的1/3左右
                if row.find(word) < (len(row) / 3):
                    # 如果是这样，那么就是第二种方案
                    method = 2
                    keyword = word
    data = {}
    key = ""
    # 这里负责找 到歌词和歌手
    if method == 1:
        # 用一个flag来判断类型
        key = row[row.find("听") + 1:]
    elif method == 2:
        # 这里找到了关键词就直接截取即可
        key = row[row.find(keyword) + len(keyword):]

    data['key'] = key

    # 这里执行一下添加操作的命令
    sql = "UPDATE chat SET theoption='音乐' WHERE QQ='" + str(QQ) + "'"
    sql_dml(sql)

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(80, 'music', current_arg=data or '')

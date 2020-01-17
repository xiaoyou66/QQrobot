from jieba import posseg
from .picture import get_img
import sys
sys.path.append('.../')
from  nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand


@on_command('imgface', aliases=( '图片'))  # 这里是命令的几个关键词
async def imgface(session: CommandSession):
    # 获取到关键词的内容
    key = session.get('key', prompt='')
    # 这里在加上QQ作为关键词，避免下载冲突
    key['QQ'] = session.ctx['user_id']
    # 把获取到的关键词传入函数
    if 'key' in key and key['key']:
        # 这里写一个逻辑用来判断你这个是不是关键词
        key_list = ['日历', '动漫', '风景', '美女', '游戏', '影视', '动态', '唯美', '设计', '可爱', '汽车', '花卉', '动物', '节日', '人物', '美食',
                    '水果', '建筑', '体育', '军事', '其他', '王者荣耀', '护眼']
        kkey_list=['风景','美女','游戏','动漫','影视','明星','汽车','动物','人物','美食','宗教','背景']
        if not key['key'] in key_list and key['type']=='bizhi':
            key['notkey']=1
            await session.send("目前数据库只有25893张图片，所以这个关键词可能找不到你想要的内容，建议发送默认的关键词获取你想要的图片\n提示:发送\"壁纸关键词\"就可以得到关键词")
        if not key['key'] in kkey_list and key['type'] == '4kbizhi':
            key['notkey'] = 1
            await session.send("目前数据库只有17679张图片，所以这个关键词可能找不到你想要的内容，建议发送默认的关键词获取你想要的图片\n提示:发送\"4K壁纸关键词\"就可以得到关键词")
        # 先判断是否需要张数
        if 'num' not in key:
            # 这里只发送一张图片
            await session.send("关键词:" + key['key']+" 张数:1"+" 类型:"+key['type'])
            key['num'] = 1
            imgs = await get_img(key)
            if imgs:
                # await session.send(imgs[0])
                await session.send("[CQ:image,file=myimage/" + imgs[0] + "]")
            else:
                await session.send("[CQ:face,id=5]下载图片出错!")
        else:
            await session.send("关键词:" + key['key'] + " 张数:" + key['num']+" 类型:"+key['type'])
            key['num'] = change_to_int(key['num'])
            if key['num'] >= 5:
                key['num'] = 1
                await session.send("[CQ:face,id=212]最多只能发四张,默认只返回一张!")
            imgs = await get_img(key)
            if imgs:
                for i in imgs:
                    if i != 'null':
                        # await session.send(i)
                        await session.send("[CQ:image,file=myimage/" + i + "]")
                    else:
                        await session.send("[CQ:face,id=5]下载图片出错!")
            else:
                await session.send("[CQ:face,id=5]出现错误,无法获取到图片！")
    else:
        await session.send("[CQ:face,id=174]没有提取到关键词")


# 转换数字
def change_to_int(key):
    # 数字比较好转
    if key.isdigit():
        return int(key)
    else:
        # 去掉量词
        str = key[:-1]
        if str == "一":
            return 1
        elif str == "二":
            return 2
        elif str == "三":
            return 3
        elif str == "四":
            return 4
        elif str == "两":
            return 2
        else:
            return 5


@imgface.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            if not isinstance(stripped_arg, dict):
                key = {}
                key["key"] = stripped_arg
                key["type"] = 'img'
                session.state['key'] = key
            else:
                session.state['key'] = stripped_arg
        return

# 这里专门负责图片搜索
@on_natural_language(keywords={'图片', '照片', '相片', '图', '照', '表情', '表情包', '风景','壁纸'})
async def _(session: NLPSession):
    # 这里设置关键词，用于获取内容
    key_list = ['图片', '照片', '相片', '图', '表情', '表情包', '风景','壁纸']
    # 这里是涉及到看等一些动词的情况
    watch_list = ['看看', '看', '展示', '显示', '康康']
    # 这里是图片的量词
    img_count = ['张', '份']
    # 特别的情况（来张，或来份）
    img_special = ['来张', '来份', '来个', '给我个','开张']
    # vlist动词列表
    v_list = ['要']
    # 去掉消息首尾的空白符
    stripped_msg = session.msg_text.strip()
    # 对消息进行分词和词性标注
    words = posseg.lcut(stripped_msg)
    # 设置字典
    content = {}
    # 设置图片格式
    content['type'] = "img"
    # 这里直接手动找量词，避免歧义(注意数字后面必须接张或份)
    img = 0  # 这里用来判断量词和图片各在什么位置 主要用来处理 锤子图片给我三张 的情况
    num = 0
    img_name = ""
    for i in range(0, len(words)):
        # 这里是数字量词情况
        if words[i].flag == 'm' and (words[i].word).isdigit() and isquan(words[i + 1].word, img_count):
            content['num'] = words[i].word
            if num == 0:
                num = i

        # 这里处理普通量词
        if words[i].flag == 'm' and not (words[i].word).isdigit():
            # 找到了量词就不要在找了
            if 'num' not in content:
                if isquan(words[i].word, img_count):
                    content['num'] = words[i].word
            if num == 0:
                num = i

        # 这里判断其他的类型
        if words[i].word == '表情' and words[i+1].word == '包':
            content['type'] = "face"

        # 这里找一下图片的位置
        if words[i].word in key_list:
            if img == 0:
                img = i
                img_name = words[i].word

    # 处理类似于 找几张张三丰的照片
    key = ""
    flag = 0
    if 'num' in content and img > num:
        for word in words:
            # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
            if word.flag == 'm' or isquan(word.word, img_count):
                flag = 1
            elif word.word == '的':
                flag = 2
            # 这里是真的判断是不是到达了终点
            if flag == 2 and word.word in key_list:
                break
            # 这里负责拼接字符串
            if flag == 1 or flag == 2:
                # 这里把量词去掉(去掉找出来的量词)，并且避免去掉 张三丰之类的内容
                if (word.flag != 'm' or word.word != content['num']) and word.word != '的':
                    key += word.word
    else:
        key = stripped_msg[:stripped_msg.find(img_name)]
    # 这里负责处理没有数量词的情况
    if 'num' not in content:
        flag = 0
        method = 0
        key = ""
        # 这里用于判断各种逻辑
        for word in words:
            if word.word in img_count:
                method = 1
                # 这里是处理看，看看之类的动词情况
            elif word.word in watch_list:
                method = 2
        # 这里负责处理分词错误的情况
        if method == 0:
            for word in img_special:
                if word in stripped_msg:
                    method = 3
            if method == 0:
                # 最后我们尝试找一下动词
                for word in words:
                    if word.flag == "v" and word.word in v_list:
                        method = 4
        # 这里负责处理有张或份的逻辑
        if method == 1:
            for word in words:
                # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
                if word.word in img_count:
                    flag = 1
                elif word.word == '的':
                    flag = 2
                # 这里是真的判断是不是到达了终点
                if flag == 2 and word.word in key_list:
                    break
                # 这里负责拼接字符串
                if flag == 1 or flag == 2:
                    if (word.word not in img_count) and word.word != '的':
                        key += word.word
        # 这里负责有动词看或者展示的情况
        elif method == 2:
            for word in words:
                # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
                if word.word in watch_list:
                    flag = 1
                elif word.word == '的':
                    flag = 2
                # 这里是真的判断是不是到达了终点
                if flag == 2 and word.word in key_list:
                    break
                # 这里负责拼接字符串
                if flag == 1 or flag == 2:
                    if word.word not in watch_list and word.word != '的':
                        key += word.word
        # 这里处理一下来张崩坏的情况(分词错误)
        elif method == 3:
            for word in img_special:
                if word in stripped_msg:
                    key = stripped_msg[stripped_msg.index(word) + len(word):]

        # 这里处理动词情况
        elif method == 4:
            # 动词前面要有代词的flag
            # 删除最后的图片关键词
            if words[-1].word in key_list:
                words.pop()
            # 删除的
            if words[-1].word == "的":
                words.pop()
            flag = 0
            for word in words:
                if word.flag == 'r':
                    flag = 1
                if flag == 1 and word.flag == 'v':
                    flag = 2
                    continue
                if flag == 2:
                    key += word.word
        # 这个是最后的处理逻辑
        else:
            # 删除最后的图片关键词
            if words[-1].word in key_list:
                words.pop()
            # 删除的
            if words[-1].word == "的":
                words.pop()
            for word in words:
                key += word.word
    # 判断是普通壁纸还是4K壁纸
    if '壁纸' in stripped_msg:
        content['type'] = 'bizhi'
        key = key.replace("壁纸", "")
    if '4k' in stripped_msg or '4K' in stripped_msg:
        content['type'] = '4kbizhi'
        key = key.replace("壁纸", "")
        key = key.replace("4k", "")
        key = key.replace("4K", "")
    # 这里把张去掉 是否去掉张
    delz = 0
    if key:
        words = posseg.lcut(key)
        # 去掉量词
        if words[0].word in img_count:
            del words[0]
        # 去掉数字
        if 'num' in content:
            # 去掉 小白我要15张小白的照片 的张 前提
            if content['num'] + "张" in stripped_msg and content['num'].isdigit():
                delz = 1
            # 把量词去掉
            if words[0].word == content['num']:
                del words[0]
        # 这里把后面的图片给去掉
        if words[-1].word in key_list:
            words.pop()
        # 这里想办法去掉的
        if words[-1].word == "的":
            words.pop()
        # 拼接字符串
        key = ""
        for word in words:
            key += word.word
    # 发送命令前先删除表情包
    if  content['type']=="face":
        key=key.replace("表情包","")
    # 这里拼接字符串
    if delz == 1 and key[:1]=='张':
        content['key'] = key[1:]
    else:
        content['key'] = key
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'imgface', current_arg=content or '')


# 判断是否包含关键词
def isquan(key, content):
    for word in content:
        if word in key:
            return True
    return False

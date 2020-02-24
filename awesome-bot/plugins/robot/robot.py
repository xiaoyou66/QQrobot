# coding=utf8
import random
import urllib.request
import hashlib
import requests
import urllib, re, json
from os import path

#茉莉机器人
def moli(text):
    url = "http://i.itpk.cn/api.php?question=" + text + "&api_key=e8cf5bb5c4e968e0e688148426084cac&api_secret=wnlgf7cdxu01"
    respose = requests.get(url).text
    return respose

#青客云智能机器人
def qinyunke(text):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="+text
    respose = requests.get(url).text
    return respose.replace("{br}","\n")

#图灵机器人函数
def tulin(text):
    url="http://route.showapi.com/60-27?&showapi_appid=107983&info="+text+"&userid=123&showapi_sign=603f5a2c1306491ebdb6cb7782a10043"
    response=requests.get(url).text
    content=json.loads(response)
    return content['showapi_res_body']['text']


#小i机器人备用
def xiaoiback(text):
    url="http://5555.ibot.xiaoi.com/ibot-xiaoi-web/api/robot?&userId=yuijmloww478r&platform=web&question="+text
    content=requests.get(url).text
    content=re.search('content":"(.*?)"',content).group(1)
    content=re.sub(r'\[.*?\]', "",content)
    content=content.replace("</br>","\n",-1)
    content=content.replace("<br>","\n",-1)
    return content


#小i机器人相关
class xiaoi_bot(object):
    def __init__(self, appKey, appSecret):
        appKey = appKey
        appSecret = appSecret
        HA1 = hashlib.sha1(
            ':'.join([appKey, "xiaoi.com", appSecret]).encode("utf8")).hexdigest()
        HA2 = hashlib.sha1(u"GET:/ask.do".encode("utf8")).hexdigest()
        nonce = self.getNonce()  # ':'.join([HA1, nonce, HA2]).encode("utf8")
        sig = hashlib.sha1(
            ':'.join([HA1, nonce, HA2]).encode("utf8")).hexdigest()

        self.headers = {
            "X-Auth": "app_key=\"{0}\",nonce=\"{1}\",signature=\"{2}\"".format(
                appKey, nonce, sig)
        }

    def GetResponse(self, question, userId='test'):
        post_data = {
            "question": question,
            "userId": userId,
            "type": "0",
            "platform": "web"
        }
        post_data = urllib.parse.urlencode(post_data)
        url = "http://robot.open.xiaoi.com/ask.do?"+post_data
        request = urllib.request.Request(url, None, self.headers)
        request.add_header('Content-Type', 'text/html; charset=UTF-8')
        response = urllib.request.urlopen(request)
        return str(response.read(), 'utf8') #response.read()

    def getNonce(self):
        strs = ''
        for i in range(18):
            strs += (str(random.randint(0, 15)))
        return strs


#这个是酷Q机器人的函数

# def irobot(text):
#     try:
#         # 在读取数据前获取id
#         if (path.exists(path.dirname(__file__) + '\data.txt')):
#             f = open(path.dirname(__file__) + '\data.txt', 'r', encoding='UTF-8')  # 用特定编码打开文件
#             rowdata = f.read().split(",")
#             f.close()
#         sessionid = rowdata[1]
#         usrid = rowdata[0]
#         # 这里是发送的信息体
#         message = '{"sessionId":"' + sessionid + '","robotId":"webbot","userId":"' + usrid + '","body":{"content":"' + text + '"},"type":"txt"}'
#         # 这里可以获取
#         with open(path.dirname(__file__) + '\config.ini') as fp:
#             cookie = fp.read()
#         head = {'Cookie': cookie}
#         message = urllib.parse.quote(message, safe='/', encoding=None, errors=None)
#         url = "http://i.xiaoi.com/robot/webrobot?&data=" + message
#         # 这里负责把cookie载入
#         respose = requests.get(url, headers=head, timeout=5).text
#         # 字符串分割
#         data = respose.split("")
#
#         # #下面这段代码是保存数据
#         if (not path.exists(path.dirname(__file__) + '\data.txt')):
#             savedata = json.loads(data[0])
#             f = open(path.dirname(__file__) + '\data.txt', 'w', encoding='UTF-8')  # 用特定编码打开文件
#             f.write(savedata['userId'] + "," + savedata['sessionId'])
#             f.close()
#
#         # #这里是获取数据并返回
#         data = json.loads(data[len(data) - 2])
#         data = data['body']['content'].strip()
#
#         # 这里使用正则表达式匹配把[开头]结尾的都去掉
#         data = re.sub('\[.*?\]', "", data)
#         # 这里把换替换
#         return data.replace("</br>", "\n")
#
#     except Exception:
#         return None
#

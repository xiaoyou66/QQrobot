#小i机器人测试函数
import random
import urllib.request
import hashlib
import requests
import urllib, re, json
from os import path



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
            "platform": "weixin"
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


if __name__=="__main__":

    # bot = xiaoi_bot("open1_hcIem0YcTvHf","aP0ZsvpTGBv4MjpDYPVJ")
    # data = bot.GetResponse("来个笑话", "test")
    print("test")
    # text="国内新闻"
    # url="http://5555.ibot.xiaoi.com/ibot-xiaoi-web/api/robot?&userId=123&platform=web&question="+text
    # content=requests.get(url).text
    # print(re.search('content":"(.*?)"',content).group(1))

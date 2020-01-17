# -*- coding: utf-8 -*-
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import threading
import json,os,time
import ali_speech
from ali_speech.callbacks import SpeechSynthesizerCallback
from ali_speech.constant import TTSFormat
from ali_speech.constant import TTSSampleRate
import requests
import re,random,configparser
from urllib.parse import unquote
from bs4 import BeautifulSoup


class MyCallback(SpeechSynthesizerCallback):
    # 参数name用于指定保存音频的文件
    def __init__(self, name):
        self._name = name
        self._fout = open(name, 'wb')
    def on_binary_data_received(self, raw):
        print('MyCallback.on_binary_data_received: %s' % len(raw))
        self._fout.write(raw)
    def on_completed(self, message):
        print('MyCallback.OnRecognitionCompleted: %s' % message)
        self._fout.close()
    def on_task_failed(self, message):
        print('MyCallback.OnRecognitionTaskFailed-task_id:%s, status_text:%s' % (
            message['header']['task_id'], message['header']['status_text']))
        self._fout.close()
    def on_channel_closed(self):
        print('MyCallback.OnRecognitionChannelClosed')
def process(client, appkey, token, text, audio_name):
    callback = MyCallback(audio_name)
    synthesizer = client.create_synthesizer(callback)
    synthesizer.set_appkey(appkey)
    synthesizer.set_token(token)
    synthesizer.set_voice('xiaoyun')
    synthesizer.set_text(text)
    synthesizer.set_format(TTSFormat.WAV)
    synthesizer.set_sample_rate(TTSSampleRate.SAMPLE_RATE_16K)
    synthesizer.set_volume(50)
    synthesizer.set_speech_rate(0)
    synthesizer.set_pitch_rate(0)
    try:
        ret = synthesizer.start()
        if ret < 0:
            return ret
        synthesizer.wait_completed()
    except Exception as e:
        print(e)
    finally:
        synthesizer.close()
def process_multithread(client, appkey, token, number):

    thread_list = []
    for i in range(0, number):
        text = "这是线程" + str(i) + "的合成。"
        audio_name = "sy_audio_" + str(i) + ".wav"
        thread = threading.Thread(target=process, args=(client, appkey, token, text, audio_name))
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()

#读取配置
def getconfig():
    data={}
    config = configparser.ConfigParser()
    config.read('config.ini',encoding='utf-8')
    data["key"] = config.get('aliyun','appkey')
    data["AccessKey"] = config.get('aliyun','AccessKey')
    data["AccessKeySecret"] = config.get('aliyun','AccessKeySecret')
    # print(data)
    return data


async def speakvoice(key: str) -> str:
    try:
        data=getconfig()
        filepath = os.path.dirname(__file__) + '\data.txt'
        if(key=='鉴权'):
            # 创建AcsClient实例
            client = AcsClient(
                data["AccessKey"],
                data["AccessKeySecret"],
                "cn-shanghai"
            )
            # 创建request，并设置参数
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')
            response = client.do_action_with_exception(request)
            content = json.loads(response)
            token = content['Token']['Id']
            with open(filepath, "w") as fp:
                fp.write(token)
            return '[CQ:face,id=101]鉴权成功，你现在可以开始发语音了！'
        with open(filepath,"r")  as fp:
            token=fp.read()
        client = ali_speech.NlsClient()
        # 设置输出日志信息的级别：DEBUG、INFO、WARNING、ERROR
        client.set_log_level('INFO')
        appkey =data['key']
        text =key
        audio_name = 'data/record/mymusic/'+'1.mp3'
        process(client, appkey, token, text, audio_name)
        return "[CQ:record,file=mymusic/1.mp3,magic=false]"
    except (Exception):
        return "[CQ:face,id=177]出了问题，好像不能获取到数据了，请重试！"

async def AddVoice(key:str)->str:
    try:
        filepath = os.path.dirname(__file__) + '\data.txt'
        with open(filepath, "r")  as fp:
            token = fp.read()
        t = time.time()
        filename = str(int(t)) + ".mp3"
        client = ali_speech.NlsClient()
        # 设置输出日志信息的级别：DEBUG、INFO、WARNING、ERROR
        client.set_log_level('INFO')
        appkey = 'Fx9voCGViOO6mKJj'
        text = key
        audio_name = 'data/record/record/' + filename
        process(client, appkey, token, text, audio_name)
        return "[CQ:record,file=record/"+filename+",magic=false]"
    except (Exception):
        return ""


async def Getbackground(key: str) -> str:
    try:
    #设置请求的关键词
        url='http://aspx.sc.chinaz.com/tools/ajax.ashx'
        data={'action':'loadData','key':key,'cid':14}
        response=requests.post(url,data=data,timeout=5).text
        #解析json数据
        data=json.loads(response)
        #获取我们想要的结果
        data=unquote(data['html'])
        #使用正则进行匹配
        # ()这个东西表示分组，就是我们获取到()里面的数据
        srcs=re.findall("href='(.*?)'",data)
        #得到最后的结果
        if(srcs):
            #这里我们随机获取一个数据
            url=srcs[random.randint(0,len(srcs))-1]
            response=requests.get(url,timeout=5).text
            soup=BeautifulSoup(response)
            musiclist=soup.select("div[class='downbody yc'] a")
            musicurl=musiclist[random.randint(0,len(musiclist)-1)].attrs['href']
            req = requests.get(musicurl,timeout=5)
            with open('data/record/mymusic/2.mp3','wb') as code:
                code.write(req.content)
            return "[CQ:record,file=mymusic/2.mp3,magic=false]"
        else:
            return "[CQ:face,id=97]没有找到你要的音效"
    except (Exception):
        return "[CQ:face,id=97]没有找到你要的音效,或者下载失败"
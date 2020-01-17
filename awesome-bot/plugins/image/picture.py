import requests
import re
import json
import random,configparser
import os
from contextlib import closing  # 这个是图片下载的库
from threading import Thread
from bs4 import BeautifulSoup
import glob
from os import path
import MySQLdb


async def get_img(key: dict) -> list:
    # 获取到关键词
    try:
        # 先尝试获取bing的，如果没用就获取百度的
        # 这里可以获取一下bing的cookie和skey
        urls = []
        if key['type']=='img':
            with open(os.path.dirname(__file__) + '\data.txt',"r",encoding="utf-8") as fp:
                cookie = fp.read().split("\n")
            try:
                # 设置url还有cookie数据
                url = "https://cn.bing.com/images/api/custom/search?q=" + key['key'] + "&count=50&skey=" + cookie[1]
                header = {
                    'Cookie': cookie[1],
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
                # 发送请求
                respose = requests.get(url, headers=header, timeout=5).text
                # 解析为json数据，然后转换抓取一个图片
                imglist = json.loads(respose)
                imglist = imglist['value']
                # 这里随机抓取指定张数图片
                for num in range(0, key['num']):
                    urls.append(imglist[random.randint(0, 49)]['contentUrl'])
                # return urls
            except (Exception):
                # bing接口容易失效，可以采用百度的
                ranpage = random.randint(1, 50)
                url = "https://image.baidu.com/search/index?tn=baiduimage&pn=" + str(ranpage) + "&word=" + key['key']
                # 设置一下头部信息
                head = {'Host': 'image.baidu.com', 'Refer': 'https://www.google.com/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
                respose = requests.get(url, headers=head, timeout=5).text
                # 利用正则来匹配获取我们需要的数据
                pic_urls = re.findall('"objURL":"(.*?)",', respose, re.S)
                # 这里随机抓取指定张数图片
                for num in range(0, key['num']):
                    urls.append(pic_urls[random.randint(0, len(pic_urls) - 1)])
        elif key['type']=='face':
            # 这里是表情包处理代码
            url = "https://fabiaoqing.com/search/search/keyword/" + key['key']
            respose = requests.get(url, "", timeout=6).text
            soup = BeautifulSoup(respose)
            imglist = soup.select('img[class="ui image bqppsearch lazy"]')
            try:
                for num in range(0, key['num']):
                    urls.append(imglist[random.randint(0, len(imglist) - 1)].attrs['data-original'])
            except (Exception):
                return []
        #下载壁纸
        elif key['type']=='bizhi' or key['type']=='4kbizhi':
            # 判断是否是分类查找
            if 'notkey' in key:
                urls =bizhi(key['key'],key['num'],0,key['type'])
            else:
                urls=bizhi(key['key'],key['num'],1,key['type'])
    except (Exception):
        return []
    try:
        # 设置图片路径
        filepath = "data/image/myimage/"
        # filepath = os.path.abspath(os.path.join(os.getcwd(),""))+"\data\image\myimage\\"
        files = []
        # 先把文件夹清空
        filelist = glob.glob(filepath + str(key['QQ']) + "*")
        for f in filelist:
            try:
                os.remove(f)
            except:
                pass
        # 使用多线程下载图片
        threads = []  # 这里我们使用多线程，要把这些线程放到列表里
        step = 1
        for url in urls:  # 我们要下多少图片就开多少线程
            houzui=url[str(url).rfind(".")+1:]
            h_list=['jpg','png','jpeg','gif','bmp','webp']
            if houzui not in h_list:
                houzui='jpg'
            filename = str(key['QQ']) + str(step) +"."+houzui
            # 这里处理4K壁纸的情况
            is4k=0
            if key['type']=='4kbizhi':
                is4k=1
                filename=filename[:filename.rfind(".")]+".jpg"
            t = Thread(target=download(url, filepath + filename,is4k))  # 把函数加到线程里面
            files.append(filename)
            step += 1
            t.start()  # 开始线程
            threads.append(t)  # 把线程都加到列表里面，方便后面判断是否下载完毕
        for t in threads:
            t.join()  # 这里就是等待线程结束的代码
        # 这里判断图片是否下载成功
        for i in range(0, len(files)):
            if not os.path.exists(filepath + files[i]):
                files[i] = ""
        return files
    except Exception:
        return []

def download(url, filepath,is4k):
    try:
        if (os.path.exists(filepath)):
            os.remove(filepath)
        if is4k:
            with open(os.path.dirname(__file__) + '\data.txt',"r",encoding="utf-8") as fp:
                cookie = fp.read().split("\n")
            print(cookie)
            head = {"Cookie": cookie[3]}
        else:
            head={}
        # 这里是下载命令，用于下载图片
        with closing(requests.get(url=url,headers=head,stream=True, timeout=5)) as r:  # 这里就是下载图片的代码了
            with open(filepath, 'ab+') as f:  # 这里是保存图片
                for chunk in r.iter_content(chunk_size=1024):  # 下面都是下载图片数据的代码，所以不解释
                    if chunk:
                        f.write(chunk)
                        f.flush()
    except Exception:
        os.remove(filepath)


#下载壁纸
def bizhi(key,num,iskey,type):
    if type=='bizhi':
        bd='img'
    else:
        bd='4Kimg'

    if iskey==1:
        #这里是直接找tag
        #这里随机在数据库中查找一个值
        sql = "SELECT src FROM "+bd+" WHERE tag='"+key+"' ORDER BY rand() limit "+ str(num)
    else:
        #这里是查找模糊关键词
        sql = "SELECT src FROM "+bd+" WHERE title LIKE '%"+key+"%' ORDER BY rand() limit "+ str(num)
    result = sql_dql(sql)
    src = []
    if result:
        for data in result:
            src.append(data[0])
    return src



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
    print(data)
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
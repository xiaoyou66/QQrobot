import json
import requests
from os import path
async def get_weather_of_city_time(content: dict) -> str:
    return get_weather(content)

async def get_weather_of_city(city: str)->str:
    content={'city':city}
    return get_weather(content)

def get_weather(content):
    try:
        f=open(path.dirname(__file__)+'\city.json','r',encoding='UTF-8')#用特定编码打开文件
        data=f.read()#读取文件数据
        data=json.loads(data)#转换为json对象
        recommd=""
        for key in data: #遍历数据
           if key['city_name']==content['city'] or key['city_name']==content['city']+"市":
               if key['city_code']=="":
                   return "[CQ:face,id=106]该地方暂不支持查询，你可以缩小范围或者换一个地方搜索！"
               else:
                   position=0
                   if 'time' in content:
                       if content['time']=='明天':
                           position=1
                       elif content['time']=='后天':
                            position=2
                       elif content['time']=='大后天':
                            position=3
                   #这里是查找到了对应的数据,发送请求,然后获取数据
                   respose=requests.get('http://t.weather.sojson.com/api/weather/city/'+key['city_code'],timeout=5).text
                   respose=json.loads(respose)
                   if position==0:
                       data="当前时间:"+respose['data']['forecast'][position]['ymd']+respose['data']['forecast'][position]['week']+"\n数据更新时间:"+respose['cityInfo']['updateTime']
                       data+= "\n--------------------------\n天气:" + respose['data']['forecast'][position]['type'] + "        当前温度:" +respose['data']['wendu']
                       data+="\nPM2.5:"+str(respose['data']['pm25'])+"    空气质量:"+respose['data']['quality']
                       data+="\n"+respose['data']['forecast'][position]['high']+"       "+respose['data']['forecast'][position]['low']
                       data+="\n"+respose['data']['forecast'][position]['fx']+respose['data']['forecast'][position]['fl']
                       data+="\n"+respose['data']['forecast'][position]['notice']+"[CQ:face,id=21]"
                       return f"      [CQ:face,id=74]"+content['city']+"天气[CQ:face,id=75]\n"+data
                   else:
                       data = "当前时间:" + respose['data']['forecast'][position]['ymd'] + respose['data']['forecast'][position][
                           'week'] + "\n数据更新时间:" + respose['cityInfo']['updateTime']
                       data += "\n--------------------------\n天气:" + respose['data']['forecast'][position][
                           'type']+"      "+respose['data']['forecast'][position]['fx'] + respose['data']['forecast'][position]['fl']
                       data += "\n" + respose['data']['forecast'][position]['high'] + "       " + \
                               respose['data']['forecast'][position]['low']
                       data += "\n" + respose['data']['forecast'][position]['notice'] + "[CQ:face,id=21]"
                       return f"      [CQ:face,id=74]" +content['time']+ content['city'] + "天气[CQ:face,id=75]\n" + data
           # 这里是扩大或者缩小范围，用来找推荐的地点
           elif key['city_name'].find(content['city'])!=-1 or content['city'].find(key['city_name'])!=-1:
               recommd=key['city_name']
        if recommd:
            return "[CQ:face,id=32]没有找到这个地方，你是不是要找["+recommd+"]?"
        else:
            return "[CQ:face,id=32]没有找到这个地方,你在换个地方试试！"
    except (Exception):
        return "[CQ:face,id=32]好像出了点问题，你在试一下吧！"
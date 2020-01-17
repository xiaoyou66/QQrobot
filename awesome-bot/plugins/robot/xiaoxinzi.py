import json,requests
from urllib import parse
#这个接口现在几乎没用了

def xiaoxizi(text):
    city="湖南"
    nickname="小游"
    city=parse.quote(city)
    nickname=parse.quote(nickname)
    text=parse.quote(text)
    url = "http://ai3.aixxz.com/api3?city="+city+"&nickname="+nickname+"&text="+text+"&user=123"
    head = {'Authorization':'APPCODE 872ff9921e7748aaa48791ddfc7b1f9d','Content-Type':'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=head, timeout=5).text
    content=json.loads(response)
    if content['datatype']=='text':
        return response(content)

def response(data):
    return data['data']
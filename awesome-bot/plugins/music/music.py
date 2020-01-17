import requests
import json
from Crypto.Cipher import AES
import binascii
import base64
import os
import random


async def getmusic(key: dict) -> dict:
    if key['type']=="qq":
        return getQQmusic(key['key'])
    else:
        return get163(key['key'])


# 获取网易云音乐(音乐搜索)
def get163(key):
    eparams = {
        "method": "POST",
        "url": "http://music.163.com/api/cloudsearch/pc",
        "params": {"s": key, "type": 1, "offset": 0, "limit": 10},
    }
    data = {"eparams": encode_netease_data(eparams)}
    head={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    res_data = requests.post("http://music.163.com/api/linux/forward", data=data,headers=head).text
    content = json.loads(res_data)
    musiclist = content['result']['songs']
    # 这里简单的把这些歌详细的整理成json数据
    all_data={}
    datas=[]
    for music in musiclist:
        data={}
        data['name']=music['name']
        sgs=""
        for sg in music['ar']:
           sgs+=sg['name']+" "
        data['sginer']=sgs
        data['id']=music['id']
        datas.append(data)
    all_data['type'] = '163'
    all_data['result']=datas
    # 直接返回
    signs=""
    for sign in musiclist[0]['ar']:
        signs += sign['name']+" "
    all_data['singr'] = signs
    all_data['name']=musiclist[0]['name']
    all_data['id'] = musiclist[0]['id']
    return all_data


# 获取QQ音乐
def getQQmusic(key):
    url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w=" + key + "&format=json&n=10"
    resopse = requests.get(url).text
    content = json.loads(resopse)
    musiclist=content['data']['song']['list']
    # 这里简单的把这些歌详细的整理成json数据
    all_data = {}
    datas = []
    for music in musiclist:
        data = {}
        data['name'] = music['songname']
        sgs = ""
        for sg in music['singer']:
            sgs += sg['name'] + " "
        data['sginer'] = sgs
        data['id'] = music['songid']
        datas.append(data)
    all_data['result'] = datas
    all_data['type'] = 'qq'
    # 不需要精确判断，直接返回第一首歌
    #添加歌手
    signs=""
    for sign in musiclist[0]['singer']:
        signs+=sign['name']+" "
    all_data['singr']=signs
    all_data['id'] = musiclist[0]['songid']
    all_data['name']=musiclist[0]['songname']
    return all_data


# 下面是网易云音乐的一些必要函数(主要是一些加密信息)

def encode_netease_data(data) -> str:
    data = json.dumps(data)
    key = binascii.unhexlify("7246674226682325323F5E6544673A51")
    encryptor = AES.new(key, AES.MODE_ECB)
    # 补足data长度，使其是16的倍数
    pad = 16 - len(data) % 16
    fix = chr(pad) * pad
    byte_data = (data + fix).encode("utf-8")
    return binascii.hexlify(encryptor.encrypt(byte_data)).upper().decode()


def encrypted_request(data) -> dict:
    MODULUS = (
        "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
        "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
        "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
        "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
        "3ece0462db0a22b8e7"
    )
    PUBKEY = "010001"
    NONCE = b"0CoJUm6Qyw8W8jud"
    data = json.dumps(data).encode("utf-8")
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]

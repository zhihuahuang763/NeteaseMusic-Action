import requests
import base64
import json
import hashlib
from Crypto.Cipher import AES


def encrypt(key, text):
    cryptor = AES.new(key.encode('utf8'), AES.MODE_CBC, b'0102030405060708')
    length = 16
    size = len(text.encode('utf-8'))
    if size % length != 0:
        add = length - (size % length)
    else:
        add = 16
    pad = chr(add)
    text1 = text + (pad * add)
    ciphertext = cryptor.encrypt(text1.encode('utf8'))
    crypt_str = str(base64.b64encode(ciphertext), encoding='utf-8')
    return crypt_str


def md5(text):
    hl = hashlib.md5()
    hl.update(text.encode(encoding='utf-8'))
    return hl.hexdigest()


def protect(text):
    return {"params": encrypt('TA3YiYCfY2dDJQgg', encrypt('0CoJUm6Qyw8W8jud', text)),
            "encSecKey": "84ca47bca10bad09a6b04c5c927ef077d9b9f1e37098aa3eac6ea70eb59df0aa28b691b7e75e4f1f9831754919ea784c8f74fbfadf2898b0be17849fd656060162857830e241aba44991601f137624094c114ea8d17bce815b0cd4e5b8e2fbaba978c6d1d14dc3d1faf852bdd28818031ccdaaa13a6018e1024e2aae98844210"}


s = requests.Session()
header = {}
url = "https://music.163.com/weapi/login/cellphone"
url2 = "https://music.163.com/weapi/point/dailyTask"
url3 = "https://music.163.com/weapi/v1/discovery/recommend/resource"
login_data = {
    "phone": input(),
    "countrycode": "86",
    "password": md5(input()),
    "rememberLogin": "true",
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    "Referer": "https://music.163.com/",
    "Accept-Encoding": "gzip, deflate",
}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    "Referer": "https://music.163.com/",
    "Accept-Encoding": "gzip, deflate",
    "Cookie": "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=8.10.90; channel=netease; __remember_me=true;"
}

res = s.post(url=url, data=protect(json.dumps(login_data)), headers=headers2)
temp_cookie = res.cookies
obj = json.loads(res.text)
if obj['code'] == 200:
    print("登录成功！")
else:
    print("登录失败！请检查密码是否正确！" + str(obj['code']))
    exit(obj['code'])

res = s.post(url=url2, data=protect('{"type":0}'), headers=headers)
obj = json.loads(res.text)
if obj['code'] != 200 and obj['code'] != -2:
    print("签到时发生错误：" + obj['msg'])
else:
    if obj['code'] == 200:
        print("签到成功，经验+" + str(obj['point']))
    else:
        print("重复签到")

res = s.post(url=url3,
             data=protect('{"csrf_token":"' + requests.utils.dict_from_cookiejar(temp_cookie)['__csrf'] + '"}'),
             headers=headers)
obj = json.loads(res.text, strict=False)
for x in obj['recommend']:
    url = 'https://music.163.com/weapi/v3/playlist/detail?csrf_token=' + requests.utils.dict_from_cookiejar(temp_cookie)['__csrf']
    data = {
        'id': x['id'],
        'n': 1000,
        'csrf_token': requests.utils.dict_from_cookiejar(temp_cookie)['__csrf'],
    }
    res = s.post(url, protect(json.dumps(data)), headers=headers)
    obj = json.loads(res.text, strict=False)
    buffer = []
    count = 0
    for j in obj['playlist']['trackIds']:
        data2 = {}
        data2["action"] = "play"
        data2["json"] = {}
        data2["json"]["download"] = 0
        data2["json"]["end"] = "playend"
        data2["json"]["id"] = j["id"]
        data2["json"]["sourceId"] = ""
        data2["json"]["time"] = "240"
        data2["json"]["type"] = "song"
        data2["json"]["wifi"] = 0
        buffer.append(data2)
        count += 1
        if count >= 310:
            break
    if count >= 310:
        break
url = "http://music.163.com/weapi/feedback/weblog"
postdata = {
    "logs": json.dumps(buffer)
}
res = s.post(url, protect(json.dumps(postdata)))
obj = json.loads(res.text, strict=False)
if obj['code'] == 200:
    print("刷单成功！共" + str(count) + "首")
    exit()
else:
    print("发生错误：" + str(obj['code']) + obj['message'])
    exit(obj['code'])

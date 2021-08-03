#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Author: Payiz
# @project: 百度图片下载器
# @File : 下载器1.0.py
# @Time : 2020/12/5 03:35:22
# 需要安装第三方库？试试下面语句(使用清华镜像源)
# pip --default-timeout=100 install -i https://pypi.tuna.tsinghua.edu.cn/simple name
# -----------------------------------

import requests
import re
import time
import os
import urllib.parse
import json

# 每次json出的数据量
page_num = 30
photo_dir = './下载结果/'  # path 地址


def getDetailImage(word, width, height):
    num = 0
    url = 'https://image.baidu.com/search/acjson?'
    string_parameters = 'tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord={0}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=&hd=&latest=&copyright=&word={0}&s=&se=&tab=&width={2}&height={3}&face=&istype=&qc=&nc=1&fr=&expermode=&nojc=&pn={1}&rn=' + str(
        page_num) + '&gsm=3c&1627926209='
    url = url + string_parameters
    # 页数
    while num < 3:
        page_url = url.format(urllib.parse.quote(word), num * page_num, width, height)
        print(page_url)
        # response = requests.get(page_url)  # , allow_redirects=False)

        headers = {
            'Accept': 'text / plain, * / *;q = 0.01',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep - alive',
            'Host': 'image.baidu.com',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/siqned-exchange;v=b3;q=0.9'
        }

        sessions = requests.session()
        sessions.headers = headers
        response = sessions.get(url, allow_redirects=True)

        regex = re.compile(r'\\(?![/u"])')
        try:
            json_data = json.loads(regex.sub(r"\\\\", response.text))  # 转义nbjk jkkjjhkjh

            for item in json_data['data']:
                URL = item['objURL']
                type = item['type']
                pic_url = baidtu_uncomplie(URL)
                print(pic_url)
                html = requests.get(pic_url, timeout=5)

                with open(word_dir2 + '/' + str(time.time()).replace('.', '1') + '.' + type, 'wb')as f:
                    f.write(html.content)
        except Exception as e:
            print('出错了:', e)
            pass

        num = num + 1
        time.sleep(10)


# 解密
def baidtu_uncomplie(url):
    res = ''
    c = ['_z2C$q', '_z&e3B', 'AzdH3F']
    d = {'w': 'a', 'k': 'b', 'v': 'c', '1': 'd', 'j': 'e', 'u': 'f', '2': 'g', 'i': 'h', 't': 'i', '3': 'j', 'h': 'k',
         's': 'l', '4': 'm', 'g': 'n', '5': 'o', 'r': 'p', 'q': 'q', '6': 'r', 'f': 's', 'p': 't', '7': 'u', 'e': 'v',
         'o': 'w', '8': '1', 'd': '2', 'n': '3', '9': '4', 'c': '5', 'm': '6', '0': '7', 'b': '8', 'l': '9', 'a': '0',
         '_z2C$q': ':', '_z&e3B': '.', 'AzdH3F': '/'}
    if (url == None or 'http' in url):
        return url
    else:
        j = url
        for m in c:
            j = j.replace(m, d[m])
        for char in j:
            if re.match('^[a-w\d]+$', char):
                char = d[char]
            res = res + char
        return res


if __name__ == "__main__":
    # 用户交互，获取输入
    words = input("请输入需要查找的关键词：若多条，可用空格分割\n").split(' ')
    print(words)
    for word in words:
        word_dir = os.path.join(photo_dir, word)
        if not os.path.exists(word_dir):
            os.makedirs(word_dir)
        widths = ['1920', ]
        heights = ['1080', ]
        for width, height in zip(widths, heights):
            word_dir2 = word_dir + '/' + (width + 'x' + height)
            if not os.path.exists(word_dir2):
                os.makedirs(word_dir2)
            getDetailImage(word, width, height)

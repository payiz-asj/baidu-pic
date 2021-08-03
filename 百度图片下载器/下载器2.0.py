#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Author: Payiz
# @project: 百度图片下载器
# @File : 下载器2.0.py
# @Time : 2020/12/5 05:03:33
# 需要安装第三方库？试试下面语句(使用清华镜像源)
# pip --default-timeout=100 install -i https://pypi.tuna.tsinghua.edu.cn/simple name
# -----------------------------------


import csv
import multiprocessing
import os
import random
import re
import time

import requests
import requests.adapters
# from 付费ip import zhiliu
# from Report_to_wechat.report import send_report
from selenium import webdriver  # 用来驱动浏览器的
from selenium.webdriver.chrome.options import Options  # 浏览器设置
# from selenium.webdriver import ActionChains  # 破解滑动验证码的时候用的 可以拖动图片
from selenium.webdriver.common.action_chains import ActionChains  # 鼠标悬停
from selenium.webdriver.common.by import By  # 定位器 按照什么方式查找，By.ID,By.CSS_SELECTOR
# 判断器  和下面WebDriverWait一起用的
from selenium.webdriver.support import expected_conditions as ec
# 选择器，两种方法任选其一，都是指向同一个文件
# from selenium.webdriver.support.ui import Select
# 键盘操作
from selenium.webdriver.support.wait import WebDriverWait  # 浏览器等待对象，等待页面加载某些元素

# 读文件，建立用户请求头
all_user_agents = []
with open("./请求头.txt", 'r', encoding='utf-8') as f:
    for i in f:
        all_user_agents.append(i.replace("\n", '').replace('\r', ''))


# 获取一个图片
def get_baidu_pic(keyword, select_size=1, pages=1):
    #########################################################################
    # 接口说明：
    # keyword                   搜索的图片关键词
    # select_size               筛选尺寸：1 全部尺寸  2 特大  3 大  4 中  5 小
    # pages                     爬取页数：一般1页含20-50个图片
    #########################################################################

    # 目标网址
    url = 'https://image.baidu.com/'

    # 0.建立浏览器对象，并设置参数
    chrome_options = Options()
    # 关于窗口
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    # chrome_options.add_argument("--start-maximized")  # 窗口最大化
    # chrome_options.add_argument('window-size=100x100')  # 自定义窗口大小
    chrome_options.add_argument('--headless')  # 后台运行
    # 关于页面加载
    chrome_options.add_argument('--no-sandbox')  # 禁止消息框
    chrome_options.add_argument("--disable-infobars")  # 禁止警告语
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # 另一种不加载图片的方法
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # 增加扩展
    # chrome_options.add_extension(extension_path)
    # chrome_options.add_argument("--disable-dev-shm-usage") # 这个不知道是什么
    # 设置中文
    chrome_options.add_argument('lang=zh_CN.UTF-8')

    # 添加请求头和代理ip
    # global ua
    # global all_ips
    # ip = random.choice(all_ips)
    # chrome_options.add_argument('user-agent=%s'%ua.random())
    # chrome_options.add_argument('--proxy-server='+ip)
    global all_user_agents
    chrome_options.add_argument('user-agent={}'.format(random.choice(all_user_agents)))
    # chrome_options.add_argument('Authorization="token 5325ebf07a0cbebf60780f4ebd016e7b4023065f"')
    # chrome_options.add_argument('Referer="https://statistic.hackathon2020eastchina.top/"')

    # 创建浏览器对象
    browser = None
    try:
        browser = webdriver.Chrome(options=chrome_options)
    except Exception as message:
        print('创建浏览器对象失败，错误代码：', message)

    result = []  # 结果列表
    try:
        # 1.打开网页
        browser.get(url)
        time.sleep(0.2)
        # 2.输入需要查找的图片名
        wait = WebDriverWait(browser, 10, 0.1)
        wait.until(ec.presence_of_all_elements_located((By.ID, "kw")))
        inputs = browser.find_element_by_id("kw")
        inputs.send_keys(keyword)

        # 4.输入完信息后，执行查询操作
        # inputs.send_keys(Keys.ENTER)  # '按下'回车键，这个网站此方法不行，会跳转到别的网站
        browser.find_element_by_class_name("s_newBtn").click()  # 点击'查询'

        # 5. 开始加载网页获取目标图片
        try:
            # 筛选尺寸
            # 等待加载
            wait = WebDriverWait(browser, 10, 0.1)
            wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, "sizeFilter")))
            # 鼠标悬停
            element = browser.find_element_by_class_name('sizeFilter')
            actions = ActionChains(browser)
            actions.move_to_element(element).perform()
            # 选择尺寸，并点击
            time.sleep(0.3)
            choose_size = browser.find_element_by_xpath(
                '/html/body/div[1]/div[4]/div[2]/div/div[2]/div/div[2]/ul/li[{}]'.format(str(select_size)))
            choose_size.click()
            # 加载图片
            for one_page in range(1, pages + 1):
                # 获取该页
                wait = WebDriverWait(browser, 10, 0.1)
                wait.until(ec.presence_of_all_elements_located((By.ID, "imgid")))
                # time.sleep(0.5)
                # 等待该页中所有图片加载完毕
                page_item = '//*[@id="imgid"]/div[{}]/ul'.format(str(one_page))
                wait = WebDriverWait(browser, 10, 0.1)
                # 取得该页所有图片
                wait.until(ec.presence_of_all_elements_located((By.XPATH, page_item)))
                imgitems = browser.find_element_by_xpath(page_item).find_elements_by_class_name("imgitem")
                # print("第{}页共有{}张图片：".format(one_page, len(imgitems)))
                for i in imgitems:
                    title = i.get_attribute('data-title').replace('<strong>', '').replace('</strong>', '')
                    pic_url = i.get_attribute('data-objurl')
                    # print(title, pic_url)
                    result.append({"title": title, "pic_url": pic_url})
                # time.sleep(0.3)
                browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滑到底部

        except Exception as message:
            print('定位报错：', message)
        finally:
            # source = browser.page_source
            # content = parsel.Selector(source)
            # print('打开成功：', keyword)
            # # print(source)
            pass

    except Exception as e:
        print('打开失败：', keyword)
        print('打开网页失败，网址：{}  错误代码：'.format(url), e)
    finally:
        # 等待几秒
        # time.sleep(10)
        # 关闭浏览器对象
        browser.close()
        return result



def error_handler(e):
    print('多进程出错啦！')
    print(dir(e), "\n")
    print("-->{}<--".format(e.__cause__))

# 下载一个图片
def down_load_one_pic(file_path, name, url):
    def validateTitle(title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    try:
        # 设置重连次数
        requests.adapters.DEFAULT_RETRIES = 5
        ses = requests.Session()
        # 设置连接活跃状态为False
        ses.keep_alive = False
        global all_user_agents
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'If-Modified-Since': 'Thu, 24 Jan 2019 11:06:45 GMT',
            # 'If-None-Match': '56de0e5b196e494a8dfbe1f638eefd7e',
            # 'Upgrade-Insecure-Requests': '1',
            'user-agent': random.choice(all_user_agents)
        }

        res = requests.get(url, headers=head, timeout=10)
        # print("正在访问：", name, url)
        if res.status_code == 200 or res.status_code == 403:
            # print(res.text)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            ss = name if len(name) < 30 else name[0:30]
            ss = validateTitle(ss)
            path = file_path + '/' + ss + '.png'
            with open(path, 'wb') as f:
                f.write(res.content)
            # # with open(file_path, 'a+', newline='', encoding='utf-8-sig')as f:
            #     writer = csv.writer(f)
            #     writer.writerow([prox, origin_ip, where, datetime.datetime.now()])
            print("照片", ss, "下载成功")
        else:
            print('\n!!! 请求成功，但网页返回错误代码：{},网址{}'.format(str(res.status_code), url))
        # 关闭请求  释放内存
        res.close()
        del res
    except Exception as e:
        print("\n!!! 请求超失败，错误代码：{}，网址{}".format(e, url))
        time.sleep(5)


if __name__ == '__main__':
    start = time.time()
    # 用户交互，获取输入
    keyword = input("请输入需要查找的关键词：若多条，可用空格分割\n").split(' ')
    print(keyword)
    size = int(input("请输入尺寸：如 1 全部尺寸  2 特大  3 大  4 中  5 小 ，默认1\n"))
    count = int(input("请输入数量：默认：20\n"))
    # file_path = input("请输入下载地址\n")
    file_path = "./下载结果/"
    # 处理交互数据
    if keyword == '':
        keyword = "404"    # 哈哈哈
    if size not in [1, 2, 3, 4, 5]:
        size = 1
    if not 0 < count < 1000:
        count = 20
    pages = count // 30 + 1
    # 获取图片
    print("开始获取图片，请稍等💖💖💖")
    all_keywords = []
    for kw in keyword:
        print("正在获取关键词： ", kw,"  相关的图片...")
        get_one = {}
        get_one['key_word'] = kw
        get_one['file_path'] = file_path + kw
        get_one['all_pic'] = get_baidu_pic(kw, size, pages)[0:len(keyword)*count]
        all_keywords.append(get_one)

    print("开始下载啦！😘😘😘")
    # 测试：单进程下载
    # for i in all_keywords:
    #     print("正在下载：", i['key_word'])
    #     for j in i['all_pic']:
    #         down_load_one_pic(i['file_path'], j['title'], j['pic_url'])
    #     # break
    # # break

    # 多进程下载
    params = []
    for one in all_keywords:
        for one_pic in one['all_pic']:
            params.append((one['file_path'], one_pic['title'], one_pic['pic_url']))

    pool = multiprocessing.Pool(processes=32)
    res = pool.starmap_async(func=down_load_one_pic, iterable=params, error_callback=error_handler)
    pool.close()
    pool.join()

    print('\n------------------------------------------------')
    end = time.time()
    print('程序结束，总共耗时：', end - start, '秒')
    print('\n欢迎下次再来！❤')

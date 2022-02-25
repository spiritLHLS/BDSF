import requests
import random
import re
import time
import json
from lxml import html
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from requests.adapters import HTTPAdapter
import moniter_time



def input_dependence():
    global url, headers, driver, s
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    url = 'https://search.bilibili.com/article?keyword=%E4%BA%92%E5%8A%A8%E6%8A%BD%E5%A5%96%E5%90%88%E9%9B%86&from_source=websuggest_search&order=pubdate'
    headers = {
        'User-Agent': USER_AGENT
    }
    # 设置超时重试
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))
    # 启动浏览器内核
    opt = FirefoxOptions()
    opt.headless = True
    ser = Service("geckodriver")
    driver = Firefox(service=ser, options=opt)
    driver.set_page_load_timeout(300)

def get_detail(dynamic_id):
    durl = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail'+'?dynamic_id='+str(dynamic_id)
    ress = s.get(durl, headers=headers, timeout=10).json()
    return ress

def load_driver(url):
    global driver
    try:
        driver.get(url)
        return driver
    except TimeoutException:
        time.sleep(5)
        driver.delete_all_cookies()
        try:
            driver.get(url)
            return driver
        except TimeoutException:
            print('timeout')
            return


def get_topic():
    global title1, url_list1, title2, url_list2
    res1 = s.get(url=url, headers=headers, timeout=10)
    time.sleep(random.uniform(3, 5))
    tree1 = html.fromstring(res1.text)
    title1 = tree1.xpath('//*[@id="article-list"]/ul/li[1]/div/div[1]/a/@title')
    url_list1 = tree1.xpath('//*[@id="article-list"]/ul/li[1]/div/div[1]/a/@href')
    print(title1[0], url_list1[0])
    title2 = tree1.xpath('//*[@id="article-list"]/ul/li[2]/div/div[1]/a/@title')
    url_list2 = tree1.xpath('//*[@id="article-list"]/ul/li[2]/div/div[1]/a/@href')
    print(title2[0], url_list2[0])
    print('---------------------------\n')

def merge_data(res2, datas, times):
    soup = BeautifulSoup(res2.text, "html.parser")
    for link in soup.find_all('a'):
        t_url = link.get('href')
        try:
            if 't.bilibili.com' in t_url:
                try:
                    print(t_url)
                    try:
                        did = re.findall('https://t.bilibili.com/(.*?)\?', t_url)[0]
                    except:
                        did = t_url[23:]
                    # 获取具体动态内容
                    res3 = get_detail(did)
                    time.sleep(random.uniform(4, 5))
                    if res3['code'] == 0:
                        try:
                            card = res3['data']['card']['card']
                        except:
                            card = None
                        try:
                            dyid = str(res3['data']['card']['desc']['dynamic_id'])
                        except:
                            dyid = did
                        try:
                            rid = res3['data']['card']['desc']['rid']
                        except:
                            rid = ""
                        try:
                            create_time = res3['data']['card']['desc']['timestamp']
                        except:
                            create_time = 0
                        try:
                            uid = res3['data']['card']['desc']['uid']
                        except:
                            uid = None
                        try:
                            type = res3['data']['card']['desc']['type']
                        except:
                            type = ""
                        try:
                            des = json.loads(card)['item']['description']
                        except:
                            des = ""
                        try:
                            hasOfficialLottery = res3['data']['card']['extension']['lott']
                        except:
                            hasOfficialLottery = ""
                        try:
                            uname = res3['data']['card']['desc']['user_profile']['info']['uname']
                        except:
                            uname = ''
                        try:
                            ctrl = json.loads(res3['data']['card']['extend_json'])['ctrl']
                        except:
                            ctrl = []
                        data = {
                            'lottery_info_type': 'sneaktopic',
                            'create_time': create_time,
                            'uids': [uid],
                            'uname': uname,
                            'ctrl': ctrl,
                            'dyid': dyid,
                            'rid': rid,
                            'des': des,
                            'type': type,
                            'hasOfficialLottery': hasOfficialLottery
                        }
                        print(data)
                        datas.append(data)
                except Exception as e:
                    print('错误类型是', e.__class__.__name__)
                    print('错误明细是', e)
                    print("{} 报错".format(t_url))
        except Exception as e:
            print('错误类型是', e.__class__.__name__)
            print('错误明细是', e)

    # print(len(datas))
    # print(len(times))
    if len(times) == len(datas):
        for k, m in zip(datas, times):
            k['draw_time'] = m
    else:
        try:
            for i in range(0, times):
                datas[i]['draw_time'] = times[i]
        except:
            print("无")
    return datas

def find_time(url):
    load_driver(url)
    # wait = WebDriverWait(driver, 5, 0.1)
    # wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="read-article-holder"]')))
    time.sleep(random.uniform(3, 5))
    try:
        article = driver.find_element(By.XPATH, '//*[@id="read-article-holder"]').text
    except:
        try:
            article = driver.find_element(By.CLASS_NAME, 'content-full').text
        except:
            driver.close()
            return
    sents = article.split("\n")
    temp = sents.copy()
    times = []
    for i in temp:
        if "等奖" in i or '偷塔' in i or '问题' in i or '最新的' in i or '关注' in i or '按照' in i or '提出' in i \
                or "整理不易" in i or '习惯' in i or "欧气" in i or 'deo/' in i or "官方" in i or "指引" in i  \
                or "若有" in i or "事项" in i:
            sents.remove(i)
            continue
        if len(i) <= 2:
            sents.remove(i)
            continue
    for i in sents:
        try:
            times.append(moniter_time.process_tran(i[-16:]))
        except:
            times.append(moniter_time.process_tran(i))
    print(len(times))
    return times


def get_topic_info():
    input_dependence()
    get_topic()
    # 最新
    time.sleep(random.uniform(7, 11))
    datas1 = []
    times = find_time('https:' + url_list1[0])
    print(times)
    time.sleep(random.uniform(7, 11))
    res2 = s.get('https:' + url_list1[0], headers=headers, timeout=10)
    merge_data(res2, datas1, times)
    # 第二新
    time.sleep(random.uniform(7, 11))
    datas2 = []
    times = find_time('https:' + url_list2[0])
    print(times)
    time.sleep(random.uniform(7, 11))
    res2 = s.get('https:' + url_list2[0], headers=headers, timeout=10)
    merge_data(res2, datas2, times)
    # 合并
    datas = datas1 + datas2
    # 关闭浏览器内核
    driver.close()
    try:
        driver.quit()
    except:
        print("driver 已经关闭")
    return datas

#c = get_topic_info()
#print(c)
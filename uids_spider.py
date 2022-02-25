import requests
import re
import time
import json
import random
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
    global driver, headers, s
    USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
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
        return
    except TimeoutException:
        time.sleep(5)
        driver.delete_all_cookies()
        try:
            driver.get(url)
            return
        except TimeoutException:
            print('driver timeout')
            return


def find_time(url):
    time.sleep(random.uniform(5, 7))
    load_driver(url)
    # wait = WebDriverWait(driver, 5, 0.1)
    # wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="read-article-holder"]')))
    time.sleep(random.uniform(5, 7))
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
            print(i)
            sents.remove(i)
            continue
        if len(i) <= 2:
            print(i)
            sents.remove(i)
            continue
    for i in sents:
        try:
            print(i)
            tt = moniter_time.process_tran(i[-16:])
            if tt == -1:
                c = i.split(" ")[-2]
            times.append(moniter_time.process_tran(c))
        except:
            times.append(moniter_time.process_tran(i))
    print(len(times))
    return times


def get_uids_1():
    input_dependence()
    url = 'https://space.bilibili.com/{}/dynamic'.format(32210417)# uid 32210417
    load_driver(url)
    wait = WebDriverWait(driver, 10, 0.1)
    wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/div/div/div[1]/div/div/div[2]/div')))
    ID_text = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div/div[1]/div/div/div[2]/div').get_attribute('data-did')
    load_driver('https://t.bilibili.com/' + ID_text)
    wait = WebDriverWait(driver, 10, 0.1)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'mini-header__content')))
    time.sleep(random.uniform(5, 10))
    # 下滑页面加载
    i = 0
    js = "window.scrollTo(0,99999999);"
    while i < 2:  # 页面加载长度
        i += 1
        time.sleep(random.uniform(3, 5))
        driver.execute_script(js)
    # 判断是否有置顶动态
    try:
        wait = WebDriverWait(driver, 10, 0.1)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'stick')))
    except:
        print("无置顶动态")
    # driver.get('https://t.bilibili.com/' + ID_text)
    time.sleep(random.uniform(1, 3))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    datas = []
    for link in soup.find_all('a'):
        t_url = link.get('href')
        try:
            if 'b23.tv' in t_url:
                try:
                    load_driver(t_url)
                    wait = WebDriverWait(driver, 10, 0.1)
                    wait.until(EC.visibility_of_element_located((By.ID, 'internationalHeader')))
                    # driver.get(t_url)
                    t_url = driver.current_url
                    print(t_url)
                    try:
                        did = re.findall('https://t.bilibili.com/(.*?)\?', t_url)[0]
                    except:
                        # did = re.findall('https://t.bilibili.com/(.*?)', t_url)[0]
                        did = t_url[23:41]
                    print(did)
                    time.sleep(random.uniform(3, 5))
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
                            hasOfficialLottery = ''
                        try:
                            uname = res3['data']['card']['desc']['user_profile']['info']['uname']
                        except:
                            uname = ''
                        try:
                            ctrl = json.loads(res3['data']['card']['extend_json'])['ctrl']
                        except:
                            ctrl = []
                        data = {
                            'lottery_info_type': 'sneakuids',
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

    # 获取开奖时间
    times = find_time('https://t.bilibili.com/' + ID_text)
    if len(times) == len(datas):
        for k, m in zip(datas, times):
            k['draw_time'] = m
    else:
        try:
            for i in range(0, times):
                datas[i]['draw_time'] = times[i]
        except:
            print("无")
    driver.close()
    try:
        driver.quit()
    except:
        print("driver 已经关闭")
    return datas

def get_uids_2():
    input_dependence()
    url = 'https://space.bilibili.com/{}/dynamic'.format(73773270)# uid 73773270
    load_driver(url)
    # driver.get(url)
    wait = WebDriverWait(driver, 10, 0.1)
    wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/div/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div/a')))
    time.sleep(random.uniform(1, 3))
    CV_text = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div/a').get_attribute('href')
    print(CV_text)
    load_driver(CV_text)
    # driver.get(CV_text)
    time.sleep(random.uniform(5, 10))
    wait = WebDriverWait(driver, 10, 0.1)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'mini-header__content')))
    time.sleep(random.uniform(3, 4))
    # 下滑页面加载
    i = 0
    js = "window.scrollTo(0,99999999);"
    while i < 2:  # 页面加载长度
        i += 1
        time.sleep(random.uniform(3, 5))
        driver.execute_script(js)
    # 判断是否有置顶动态
    try:
        wait = WebDriverWait(driver, 10, 0.1)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'stick')))
    except:
        print("无置顶动态")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    datas = []
    for link in soup.find_all('a'):
        t_url = link.get('href')
        try:
            if 'b23.tv' in t_url or "https://t.bilibili.com/" in t_url:
                try:
                    load_driver(t_url)
                    # driver.get(t_url)
                    wait = WebDriverWait(driver, 10, 0.1)
                    wait.until(EC.visibility_of_element_located((By.ID, 'internationalHeader')))
                    time.sleep(random.uniform(3, 5))
                    t_url = driver.current_url
                    if "www.bilibili.com/video" in t_url:
                        continue
                        # try:
                        #     did = re.findall('https://www.bilibili.com/video/(.*?)\?', t_url)[0]
                        # except:
                        #     # did = re.findall('https://t.bilibili.com/(.*?)', t_url)[0]
                        #     did = t_url[31:43]
                    else:
                        print(t_url)
                        try:
                            try:
                                did = re.findall('https://t.bilibili.com/(.*?)\?tab', str(t_url))[0]
                            except:
                                did = re.findall('https://t.bilibili.com/(.*?)\?share', str(t_url))[0]
                        except:
                            did = t_url[23:41]
                        print(did)
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
                                hasOfficialLottery = ''
                            try:
                                uname = res3['data']['card']['desc']['user_profile']['info']['uname']
                            except:
                                uname = ''
                            try:
                                ctrl = json.loads(res3['data']['card']['extend_json'])['ctrl']
                            except:
                                ctrl = []
                            data = {
                                'lottery_info_type': 'sneakuids',
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
                    print(e)
                    print("{} 报错".format(t_url))
        except Exception as e:
            print('错误类型是', e.__class__.__name__)
            print('错误明细是', e)

    driver.close()
    try:
        driver.quit()
    except:
        print("已经关闭")
    return datas




#c = get_uids_1()
#print(c)
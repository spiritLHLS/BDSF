import requests
import json
import datetime
import time
import random
import os
import copy
from fastapi import APIRouter, Depends, HTTPException, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from typing import List, Set
from apscheduler.schedulers.background import BackgroundScheduler

# 导入文件
from database import engine, Base, SessionLocal
from topic_spider import get_topic_info
from uids_spider import get_uids_1, get_uids_2
import curd
import schemas
from check_des_time import rewrite_time

Base.metadata.create_all(bind=engine)
application = APIRouter()
templates = Jinja2Templates(directory='./templates')
Session = requests.session()
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
scheduler.start()

# 一些重要自定义参数
adkey = "#"
url_ip = "http://127.0.0.1:7788/"
status_input = 0


requests.packages.urllib3.disable_warnings()


def get_db(): # 数据库依赖
    try:
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()
    except Exception as e:
        print('db错误类型是', e.__class__.__name__)
        print('db错误明细是', e)
        print("error")

def input(db, lottery_info):
    try:
        headers = {"Content-Type": "application/json"}
        origin_list = requests.get("http://127.0.0.1:6767/check/get_info_by_type/BDSF", headers=headers).json()['data']
        id_list = list(origin_list.copy())
        tp = lottery_info.copy()
        for i in tp:
            if str(i['dyid']) not in origin_list:
                id_list.append(i['dyid'])
                print(i['dyid'])
            else:
                lottery_info.remove(i)
        c = requests.post("http://127.0.0.1:6767/check/set_lottery_info/?type=BDSF", json=id_list, headers=headers)
        print(c.text)
    except:
        print("未启用检索，全部入库")
    if lottery_info == []:
        print("全部已入库，不再录入")
        return
    for i in lottery_info:
        db_user = curd.get_info_by_dyid(db, dyid=str(i["dyid"]))  # 查询是否在库
        if (db_user != None):
            print("已入库，不再录入")
        else:
            print(i)
            try:
                i["dyid"] = str(i["dyid"])
            except:
                pass

            try:
                i["lottery_info_type"]
            except:
                i["lottery_info_type"] = ""

            try:
                i["create_time"]
            except:
                i["create_time"] = 0

            try:
                i["is_liked"]
            except:
                i["is_liked"] = ""

            try:
                i["uids"]
                if i["uids"] == [None]:
                    i["uids"] = []
            except:
                i["uids"] = []

            try:
                i["uname"]
            except:
                i["uname"] = ""

            try:
                i["ctrl"]
            except:
                i["ctrl"] = ""

            try:
                i["rid"]
            except:
                i["rid"] = ""
                print("错误数据动态 {}".format(i["dyid"]))
                continue

            try:
                i["des"]
            except:
                i["des"] = ""

            try:
                i["type"]
            except:
                i["type"] = ""

            try:
                i["hasOfficialLottery"]
            except:
                i["hasOfficialLottery"] = ""

            try:
                i['draw_time']
            except:
                i['draw_time'] = 0
            try:
                curd.create_info_by_code(user=i, db=db)  # 不在库创建
            except Exception as e:
                print('错误类型是', e.__class__.__name__)
                print('错误明细是', e)
                print("错误数据动态 {}".format(i["dyid"]))
                continue


def merge_topic_info(db):
    global status_input
    status_input = 1
    lottery_info = get_topic_info()
    lottery_info = rewrite_time(lottery_info)
    input(db, lottery_info=lottery_info)
    status_input = 0

def merge_uid1_info(db):
    global status_input
    status_input = 1
    lottery_info = get_uids_1()
    lottery_info = rewrite_time(lottery_info)
    input(db, lottery_info=lottery_info)
    status_input = 0

def merge_uid2_info(db):
    global status_input
    status_input = 1
    lottery_info = get_uids_2()
    lottery_info = rewrite_time(lottery_info)
    input(db, lottery_info=lottery_info)
    status_input = 0


@application.post("/set_lottery_info_by_topic/{key}", description="爬取最新专栏2个")
def input_topic_data(
                    background_tasks: BackgroundTasks,
                    key: str,
                    db: Session = Depends(get_db)
                ):
    #scheduler.add_job(func=merge_topic_info, args=(db), next_run_time=datetime.datetime.now())
    #merge_topic_info(db)
    if key == adkey and status_input == 0:
        background_tasks.add_task(merge_topic_info, db)
        #scheduler.add_job(func=merge_topic_info, args=(db), next_run_time=datetime.datetime.now())
    print('ok')
    return "OK"

@application.post("/set_lottery_info_by_uid1/{key}", description="爬取 用户 uid 32210417")
def input_uid1_data(
                    background_tasks: BackgroundTasks,
                    key: str,
                    db: Session = Depends(get_db)
                ):
    if key == adkey and status_input == 0:
        background_tasks.add_task(merge_uid1_info, db)
        #scheduler.add_job(func=merge_uid1_info, args=(db), next_run_time=datetime.datetime.now())
    #merge_uids_info(db)
    print('ok')
    return "OK"

@application.post("/set_lottery_info_by_uid2/{key}", description="爬取 用户 uid 73773270")
def input_uid2_data(
                    background_tasks: BackgroundTasks,
                    key: str,
                    db: Session = Depends(get_db)
                ):
    if key == adkey and status_input == 0:
        background_tasks.add_task(merge_uid2_info, db)
    #merge_uids_info(db)
    print('ok')
    return "OK"

# @application.get("/get_lottery_info_time/{key}")
# def get_all_info_time(key:str, db: Session = Depends(get_db)): # 查找所有用户数据
#     if key == adkey:
#         datas = curd.get_all_info(db, skip=0, limit=1000)


@application.get("/kill_selenium/{key}", description="强行停止爬虫进程")
def kill_selenium(key: str):
    if key == adkey:
        res_os = os.popen("./clear.sh")
        return res_os.read()
    else:
        return "鉴权失败"

@application.get("/get_info_by_dyid/{dyid}", description="根据dyid查找数据")
def get_info_by_dyid(dyid: str, db: Session = Depends(get_db)):
    db_user = curd.get_info_by_dyid(db, dyid=dyid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user

@application.get("/get_overdue_info/{key}", description="返回已过期数据")
def get_overdue_info(key:str, db: Session = Depends(get_db)):
    if key == adkey:
        datas = curd.get_overdue_info(db=db)
        return datas

@application.get("/get_effective_info/{key}", description="返回未过期或未识别数据")
def get_effective_info(key:str, db: Session = Depends(get_db)):
    if key == adkey:
        datas = curd.get_effective_info(db=db)
        return datas

@application.get("/get_lottery_info/{key}", description="返回所有数据")
def get_all_info(key:str, skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    if key == adkey:
        datas = curd.get_all_info(db, skip=skip, limit=limit)
        if datas != None:
            return {
                "err_msg": "",
                "lottery_info": datas
            }
        else:
            return {
                "err_msg": "error",
                "lottery_info": ""
            }
    else:
        return {
            "err_msg": "error",
            "lottery_info": ""
        }



@application.get("/delete_all/{type}&{key}", description="根据type删除记录")
def delete_all(key:str, type: str, db: Session = Depends(get_db)):
    if key == adkey:
        db_user = curd.get_all_info(db)
        print(type)
        for i in list(db_user):
            if type == str(i).split("&")[5]:
                curd.delete_id_by_code(db, str(i).split("&")[0])
                print(type == str(i).split("&")[5])
        return "删除lottery_info_type为{}的数据成功".format(type)
    else:
        return "鉴权错误"


"""
@application.get("/get_lottery_Officialinfo/")
def get_all_Officialinfo(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)): # 查找所有用户数据
    datas = curd.get_all_info_OfficialLottery(db, skip=skip, limit=limit)
    if datas != None:
        return {
            "err_msg": "",
            "lottery_info": datas
        }
    else:
        return {
            "err_msg": "error",
            "lottery_info": ""
        }

@application.get("/get_lottery_isnotOfficialinfo/")
def get_all_isnotOfficialinfo(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)): # 查找所有用户数据
    datas = curd.get_all_info_isnotOfficialLottery(db, skip=skip, limit=limit)
    if datas != None:
        return {
            "err_msg": "",
            "lottery_info": datas
        }
    else:
        return {
            "err_msg": "error",
            "lottery_info": ""
        }



@application.get("/delete_info_by_dyid/{dyid}")
def delete_info_by_dyid(dyid: str, db: Session = Depends(get_db)): # 指定用户数据删除
    db_user = curd.get_info_by_dyid(db, dyid=dyid)
    if (db_user != None):
        curd.delete_info_by_code(db, dyid=dyid)
        return "OK"
    else:
        return "不存在数据"
"""
#
# def check_only(db,r):
#     tpdyid = []
#     with open('temp.json', 'r') as fp:
#         json_data = list(json.load(fp))
#     for i in r:
#         if str(i).split("&")[2] not in tpdyid:
#             tpdyid.append(str(i).split("&")[2])
#         else:
#             curd.delete_id_by_code(db, int(str(i).split("&")[0]))
#             tp = copy.deepcopy(json_data)
#             for i in tp:
#                 if str(i).split("&")[2] in json_data:
#                     json_data.remove(str(i).split("&")[2])
#     with open('temp.json', 'w') as fp:
#         json.dump(json_data, fp, ensure_ascii=False)
#
#
#
#
# def save(datas):
#     with open("./archive_datas/datas.json", 'w', encoding='utf-8') as json_file:
#         json.dump(datas, json_file, ensure_ascii=False)
#     return "OK"
#
#
# def archive(datas):
#     with open("./archive_datas_by_days/{}.json".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[0:10] + "_" + datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')[11:]), 'w', encoding='utf-8') as json_file_d:
#         json.dump(datas, json_file_d, ensure_ascii=False)
#     return "OK"
#
#
# def save_50(datas):
#     with open("./archive_datas/50datas.json", 'w', encoding='utf-8') as json_file:
#         json.dump(datas, json_file, ensure_ascii=False)
#     return "OK"
#
#
# @application.get("/save_json/{key}", description="保存数据为json文件")
# def save_json(key:str):
#     if key == adkey:
#         datas1 = requests.get(url_ip + "lottery/get_lottery_info/?skip=0&limit=150")
#         datas2 = requests.get(url_ip + "lottery/get_lottery_info/?skip=0&limit=20000")
#         datas3 = requests.get(url_ip + "lottery/get_lottery_info/?skip=0&limit=50")
#         scheduler.add_job(func=save, args=(datas1.json()), next_run_time=datetime.datetime.now())
#         scheduler.add_job(func=archive, args=(datas2.json()), next_run_time=datetime.datetime.now())
#         scheduler.add_job(func=save_50, args=(datas3.json()), next_run_time=datetime.datetime.now())
#     return "OK"
#
#
# @application.get("/check/{key}",description="检查一次入库数据")
# def check_data(key:str, s: int, db: Session = Depends(get_db)):
#     if key == adkey:
#         r = curd.get_all_info(db)
#         scheduler.add_job(func=check_only, args=(db, r), next_run_time=datetime.datetime.now())
#         return "循环检索，删除入库超过{}天的数据，目前库内数据共{}条".format(s, len(r))
#     else:
#         return "error"

@application.get("/status_input/",description="监测爬虫进程")
def check_data():
    return status_input



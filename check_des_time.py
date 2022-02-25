from ltp import LTP
import re
import moniter_time
import time
import datetime




def rewrite_time(lottery_info):
    # 先获得时间数组格式的日期
    threeDay = (datetime.datetime.now() + datetime.timedelta(days=3))
    oneDay = (datetime.datetime.now() - datetime.timedelta(days=1))
    # 转换为时间戳
    timeStampStart = int(time.mktime(oneDay.timetuple()))
    timeStampEnd = int(time.mktime(threeDay.timetuple()))
    # res1 = requests.get("http://xxxxxxxxxxxxx/tt/get_lottery_info/xxxxxxxxx?skip=0&limit=10000").json()
    # des = []
    dict_des = {}
    # print(len(lottery_info))
    for i in lottery_info:
        if i["des"] != "":
            # j = i["des"].split("\n")
            # for k in j:
            #     des.append(k)
            try:
                if "draw_time" not in str(i):
                    dict_des[i["dyid"]] = {
                        "ori_data": i,
                        "ori_draw_time": 0,
                        "des": i["des"]
                    }
                    print(dict_des[i["dyid"]])
                    continue
                if i["draw_time"] == -1 or i["draw_time"] == 0:
                    try:
                        print(i['draw_time'])
                        dict_des[i["dyid"]] = {
                            "ori_data": i,
                            "ori_draw_time": i["draw_time"],
                            "des": i["des"]
                        }
                    except:
                        dict_des[i["dyid"]] = {
                            "ori_data": i,
                            "ori_draw_time": 0,
                            "des": i["des"]
                        }
            except Exception as e:
                print(e)
                dict_des[i["dyid"]] = {
                    "ori_data": i,
                    "ori_draw_time": 0,
                    "des": i["des"]
                }


    ltp = LTP()
    dict_time = {}
    # print(len(dict_des))
    # print("=================")
    for m in dict_des:
        real_time_list = []  # 在前一天和三天内的时间戳列表
        time_list = []  # 时间戳列表
        time_text_list = []  # 时间词列表
        try:
            tp = dict_des[m]["des"].split("\n")
            seg, hidden = ltp.seg(tp)
            srl = ltp.srl(hidden)  # , keep_empty=False
            for i, j, k in zip(srl, tp, seg):  # 词性列表， 原始数据， 分词列表
                if "TMP" in str(i):
                    # print(k)
                    for cc in i:  # 词性列表中的断句词性表， 分词
                        if cc == []:
                            continue
                        for ccc in cc:
                            if ccc[0] == "ARGM-TMP":  # 词性表中有时间
                                if ccc[1] == ccc[2]:
                                    # print(k[ccc[1]])
                                    time_text_list.append(k[ccc[1]])
                                else:
                                    ttpp = ""
                                    for tpp in k[ccc[1]:ccc[2] + 1]:
                                        ttpp += tpp
                                    # print(ttpp)
                                    time_text_list.append(ttpp)
                    # print(time_text_list)
                    for l in time_text_list:
                        a = moniter_time.tran_fi(l)  # 中文
                        b = moniter_time.process_tran(l)  # 中英混合
                        tp = re.findall('([\d零一二两三四五六七八九十]+)[.月]([\d零一二两三四五六七八九十]+)[日号]?', j)
                        c = moniter_time.tran_fi(tp[-1][0] + "月" + tp[-1][1] + "日")  # 中文部分
                        time_list.extend([a, b, c])
                    d = moniter_time.tran_fi(j)  # 中文整体
                    e = dict_des[m]["ori_draw_time"]  # 原始时间
                    time_list.extend([d, e])
        except:
            print("无效")
        try:
            for ti in time_list:
                if ti >= timeStampStart and ti <= timeStampEnd:
                    real_time_list.append(ti)
            if real_time_list != []:
                dict_time[m] = max(real_time_list)
                # print(max(real_time_list))
            else:
                dict_time[m] = dict_des[m]["ori_draw_time"]
        except:
            dict_time[m] = dict_des[m]["ori_draw_time"]

    print("!!!!!!!!!!!!!!!!!!!!!")
    # 修改数据
    tp_lottery_info = []
    for q in lottery_info:
        for p in dict_time:
            if q["dyid"] == p:
                try:
                    data = {
                        'lottery_info_type': 'sneaktopic',
                        'create_time': q["create_time"],
                        'uids': q["uids"],
                        'uname': q["uname"],
                        'ctrl': q["ctrl"],
                        'dyid': q["dyid"],
                        'rid': q["rid"],
                        'des': q["des"],
                        'type': q["type"],
                        'hasOfficialLottery': q["hasOfficialLottery"],
                        "draw_time": int(dict_time[p])
                    }
                    tp_lottery_info.append(data)
                    print("break")
                    print(data)
                    break
                except Exception as e:
                    print(e)
        data = {
            'lottery_info_type': 'sneaktopic',
            'create_time': q["create_time"],
            'uids': q["uids"],
            'uname': q["uname"],
            'ctrl': q["ctrl"],
            'dyid': q["dyid"],
            'rid': q["rid"],
            'des': q["des"],
            'type': q["type"],
            'hasOfficialLottery': q["hasOfficialLottery"],
            "draw_time": 0
        }
        tp_lottery_info.append(data)
    print("[[[[[[[[[[[[[[[[[[[[[[[[")
    return tp_lottery_info
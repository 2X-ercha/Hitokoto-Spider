# # coding=utf-8

import requests as r
import numpy as np
import csv
import json as js
import time
import pandas as pd

def read_config():  # 配置文件创建和读取
    try:
        with open('./data/_config.json') as config_js:
            config = js.load(config_js)
            return config
    except IOError:
        with open('./data/_config.json', 'w', encoding='utf-8') as config:
            configs = {
                "path": "./data/Hitokoto.csv",	        # 文件输出路径
                "times": 3000,		                # 抓取次数
                "delay": 2,		                # 抓取休眠延迟，针对一言的QPS设置
                "timeout": 60,	                # 连接超时时间（单位：秒）
                # 读取显示
                "from": True,	                # 来自什么作品
                "from_who": True,	            # 来自谁
                "creator": False,	            # 哪位用户提交的
                "created_at": False	            # 何时提交
            }
            a = js.dumps(configs, indent=4, separators=(',', ':'))
            config.write(a)
        return read_config()


def save_ids():
    ids_file = "./data/ids.npy"
    np.save(ids_file, ids)


def load_ids():
    ids_file = "./data/ids.npy"
    ids=np.load(ids_file)
    return ids

def Hitokoto_spider():  # 爬取
    try:
        cfg=read_config()
        res=r.get("https://v1.hitokoto.cn",timeout=cfg["timeout"])
        if res.status_code != 200:
            time.sleep(cfg["delay"])                          # 抓取错误时延时delay时间后重新抓取
            return Hitokoto_spider()
        data=res.json()
        if not ids[data["id"]]:
            print("{}:\t{}".format(data["id"],data["hitokoto"]))    # 输出爬取内容
            ids[data["id"]]=True

            # 自动把分类码还原为分类
            sorts = ["Animation", "Comics", "Games", "Literature", "Original", "Internet",
                     "Other", "Film and television", "Poetry", "Netease", "Philosophy", "Smart"]
            x=ord(data["type"])-97
            if 0<=x<12: sort = sorts[x]
            else: sort = "Animation"

            inputs = [data["id"], sort, data["hitokoto"], data["from"], data["from_who"], data["creator"], data["created_at"]]
            append_csv(inputs)
    except:
        save_ids()
        time.sleep(60)
        Hitokoto_spider()


def create_csv():
    cfg=read_config()
    with open(cfg["path"],"w+",newline="",encoding="utf8") as file:
        csv_file = csv.writer(file)
        head = ["id", "sort", "hitokoto", "from", "from_who", "creator", "created_at"] # 创建csv表头
        csv_file.writerow(head)


def append_csv(inputs):
    cfg = read_config()
    with open(cfg["path"],"a+",newline='',encoding="utf8") as file:
        csv_file = csv.writer(file)
        data = [inputs]
        csv_file.writerows(data)


def sort_Hitokoto():
    cfg = read_config()
    Hitokoto_data = pd.read_csv(cfg["path"])
    Hitokoto_data = Hitokoto_data.sort_values("id")
    Hitokoto_data.to_csv(cfg["path"],index=False)


def main():
    global ids
    try:
        ids=load_ids()
    except:
        ids=np.zeros(10000,dtype=bool)
        create_csv()

    cfg=read_config()
    for i in range(cfg["times"]):Hitokoto_spider()
    save_ids()
    sort_Hitokoto()


if __name__ == "__main__":
    main()
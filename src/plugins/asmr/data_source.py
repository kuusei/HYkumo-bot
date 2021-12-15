# import nonebot
import datetime
import os
import re

from nonebot import require
from nonebot.log import logger

store = require("nonebot_plugin_localstore")
plugin_data_dir = store.get_data_dir("asmr")
plugin_data_file = store.get_data_file("asmr", "my.list")

# 模式映射文件位置
method_dict = {"排除": "\expect", "排除 -f": "\expect", "我的": "", "交换": "", "临时 -f": "\\tmp"}

# 获取筛选后的列表
async def get_RJlist(myList: list, RJfilters: list):
    # 获取所有的排除列表
    dirs = await get_dirs("排除")

    # 检查并启动排除器
    filter_list = []
    for RJfilter in RJfilters:
        if f"{RJfilter}.list" not in dirs:
            return [500, f"不支持此排除器 {RJfilter}"]
        else:
            filter_list += await get_txt("排除", RJfilter)
    filter_list = list(set(filter_list))
    filter_list.sort()
    
    # 获取我自己的列表
    myList = list(set(myList))
    myList.sort()

    # 获取筛选后的列表
    myList = [_ for _ in myList if _ not in filter_list]
    return [200, myList]

async def get_dirs(method: str):
    # 拼接文件路径
    dirs = plugin_data_dir + method_dict[method]

    # 尝试创建文件夹
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    return os.listdir(dirs)


async def get_txt(method: str, filename: str):
    # 拼接文件路径
    dirs = plugin_data_dir + method_dict[method]
    # 获取已有列表
    if os.path.exists(f"{dirs}\{filename}.list"):
        with open(f"{dirs}\{filename}.list", "r+") as f:
            return [
                re.findall(r"(RJ\d{6})", _)[0]
                for _ in f.readlines()
                if re.findall(r"(RJ\d{6})", _)
            ]
    else:
        return []


async def write_txt(method: str, filename: str, RJlist: list):
    # 拼接文件路径
    dirs = plugin_data_dir + method_dict[method]

    # 尝试创建文件夹
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    # 判断权限
    rights = {False: "a+", True: "w+"}
    enforce = False
    if (method[-2:]) == "-f":
        enforce = True

    # 获取已有列表
    if not enforce:
        rlist = await get_txt(method, filename)
    else:
        rlist = []

    # 写入数据(最终数据将与输入顺序一致)
    with open(f"{dirs}\{filename}.list", rights[enforce]) as f:
        for RJ in RJlist:
            if RJ not in rlist:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                f.write(f"{RJ} {now}\n")
                logger.debug("loader 写入文本 {}".format(RJ))
    return f"好耶"

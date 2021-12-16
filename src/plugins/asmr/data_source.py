import datetime
import os
import re

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
config = Config(**global_config.dict())

# !工具
# *获取文件夹路径(会自动创建文件夹)
# @params method   模式（即文件夹位置）
async def get_dirpath(method: str):
    # 获取路径
    dirpath = os.path.join(config.dataDir, config.methodDict[method])
    # 尝试创建文件夹
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    if global_config.environment == "dev":
        logger.info(f"加载文件夹 {dirpath}")
    return dirpath


# *获取文件夹列表(注意只有文件名)
# @params method   模式（即文件夹位置）
async def get_dirfilelist(method: str):
    dirpath = await get_dirpath(method)
    if global_config.environment == "dev":
        logger.info(f"加载目录   {os.listdir(dirpath)}")
    return os.listdir(dirpath)


# *获取文件路径
# @params method   模式（即文件夹位置）
# @params filename 文件名
async def get_filepath(method: str, filename: str):
    dirpath = await get_dirpath(method)
    filepath = os.path.join(dirpath, filename + ".list")
    if global_config.environment == "dev":
        logger.info(f"加载文件   {filepath}")
    return filepath


# !基本功能
# *获取RJ列表
# @params method   模式（即文件夹位置）
# @params filename 文件名
async def get_RJlist(method: str, filename: str):
    filepath = await get_filepath(method, filename)
    if os.path.exists(filepath):
        with open(filepath, "r+") as f:
            return [
                re.findall(r"(RJ\d{6})", _)[0]
                for _ in f.readlines()
                if re.findall(r"(RJ\d{6})", _)
            ]
    else:
        return []


# *写入RJ列表
# WARN 注意所有write类型的操作method都传list
# @params method   模式和参数,第一个为模式（即文件夹位置）
# @params filename 文件名
# @params RJlist   RJ列表
async def write_RJlist(method: list, filename: str, RJlist: list):
    # 判断权限
    rights = {False: "a+", True: "w+"}
    enforce = False
    if "-f" in method:
        enforce = True

    # 获取已有列表
    if not enforce:
        rlist = await get_RJlist(method[0], filename)
    else:
        rlist = []

    # 写入数据(最终数据将与输入顺序一致)
    filepath = await get_filepath(method[0], filename)
    with open(filepath, rights[enforce]) as f:
        for RJ in RJlist:
            if RJ not in rlist:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                f.write(f"{RJ} {now}\n")
                if global_config.environment == "dev":
                    logger.info(f"写入文本   {RJ}")
    return "好耶"


# !增强功能
# *获取筛选后的列表
# @return [code: string, list: list | string]
async def get_RJlist_filter(myList: list, RJfilters: list):
    # 获取所有的排除列表
    dirs = await get_dirfilelist("排除")
    # 检查并启动排除器
    filter_list = []
    for RJfilter in RJfilters:
        if f"{RJfilter}.list" not in dirs:
            return [500, RJfilter]
        else:
            filter_list += await get_RJlist("排除", RJfilter)
    filter_list = list(set(filter_list))
    filter_list.sort()

    # 获取我自己的列表
    myList = list(set(myList))
    myList.sort()

    # 获取筛选后的列表
    myList = [_ for _ in myList if _ not in filter_list]
    return [200, myList]

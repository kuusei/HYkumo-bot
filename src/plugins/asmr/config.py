from nonebot.plugin import require
from pydantic import BaseSettings

store = require("nonebot_plugin_localstore")


class Config(BaseSettings):
    # 数据文件夹
    dataDir = store.get_data_dir("asmr")
    # 接受的模式
    methodDict = {
        "我的": "",
        "交换": "",
        "排除": "expect",
        "临时": "tmp",
    }
    methodList = list(methodDict.keys())

    class Config:
        extra = "ignore"

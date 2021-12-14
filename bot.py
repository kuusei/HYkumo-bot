#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
# 使用cqhttp插件
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
# 日志插件
from nonebot.log import logger, default_format

# 初始化日志
logger.add("error.log",
           rotation="00:00",
           diagnose=False,
           level="ERROR",
           format=default_format)

nonebot.init()
# 如果在 bot 入口文件内定义了 asgi server， nb-cli 将会为你启动冷重载模式（当文件发生变动时自动重启 NoneBot 实例）
app = nonebot.get_asgi()

# 加载 NoneBot 内置的 CQHTTP 协议适配组件
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

# 加载内建插件 /say /echo
nonebot.load_builtin_plugins()
# 加载外部插件
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")

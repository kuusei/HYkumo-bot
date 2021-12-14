# import nonebot
from nonebot import get_driver
from nonebot import on_command
# 判断规则库
from nonebot.rule import to_me
# 事件处理类型
from nonebot.typing import T_State
# 适配器的功能类
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from .config import Config


global_config = get_driver().config
config = Config(**global_config.dict())

# !注册一个消息类型的命令处理器
# @params          指定 command 参数 - 命令名
# @params rule     补充事件响应器的匹配规则
# @params priority 事件响应器优先级
echo = on_command("好耶", rule=to_me(), priority=5)

# !每当触发一个on_command时,事件处理函数是顺序执行的！
@echo.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # 例：好耶 坏耶，则args为坏耶
    args = str(event.get_message()).strip()
    if args:
        # 设置一个state的值,用于got监听这个值是否存在
        state["msg"] = args

# !"msg" 不存在时,会发送prompt,并强制接收一条新的消息再次运行当前消息处理函数。
# 效果类似reject
@echo.got("msg", prompt="好耶?")
async def handle_city(bot: Bot, event: Event, state: T_State):
    # *从state读取数据
    # Warn 这里的数据有多个来源
    # *在之前的事件响应中被存储了,则获得这个存储的数据
    # *如果在之前的事件响应中没有存储,则got会接收新消息,并将这个消息
    # !完整的存储到 "msg" 中
    echo_str = state["msg"]
    if echo_str in ["坏耶", "不好耶", "禁止好耶"]:
        # 这个函数用于结束当前事件处理函数，强制接收一条新的消息再次运行当前消息处理函数。
        # 同时别的函数是不会被触发的
        await echo.reject(f"禁止{echo_str}")
    # 异步调用事务函数
    echo_str = await get_echo(echo_str)
    # 这个函数用于结束当前事件处理函数，强制接收一条新的消息再运行下一个消息处理函数。
    await echo.finish(echo_str)


async def get_echo(city: str):
    return f"{city}好耶"

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

echo = on_command("test", rule=to_me(), priority=5)

@echo.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = event.get_message()
    for arg in args:
        await echo.send(arg.type)
    await echo.finish("结束")

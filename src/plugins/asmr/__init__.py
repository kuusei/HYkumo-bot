import re

from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.plugin import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State

from .config import Config
from .data_source import get_RJlist, get_txt, write_txt

global_config = get_driver().config
config = Config(**global_config.dict())


# !添加列表
asmr_add = on_command("asmr添加", rule=to_me(), priority=5)


@asmr_add.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["method"] = args


@asmr_add.got("method", prompt="请输入模式")
async def handle_method(bot: Bot, event: Event, state: T_State):
    if state["method"] not in ["排除", "排除 -f", "我的", "交换"]:
        await asmr_add.finish("不支持此方法")
    if state["method"] == "我的":
        state["filename"] = event.get_user_id()


@asmr_add.got("filename", prompt="请输入排除器/交换人")
async def handle_method(bot: Bot, event: Event, state: T_State):
    pass


@asmr_add.got("list", prompt="请输入列表")
async def handle_city(bot: Bot, event: Event, state: T_State):
    RJlist = state["list"]
    # 查找所有的RJ号
    RJlist = re.findall(r"(RJ\d{6})", RJlist)
    # 写入数据
    res = await write_txt(state["method"], state["filename"], RJlist)
    await asmr_add.finish(res)


# !获取列表
asmr_get = on_command("asmr获取", rule=to_me(), priority=5)


@asmr_get.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["method"] = args


@asmr_get.got("method", prompt="请输入模式")
async def handle_method(bot: Bot, event: Event, state: T_State):
    if state["method"] not in ["排除", "我的", "交换"]:
        await asmr_get.finish("不支持此方法")
    if state["method"] == "我的":
        state["filename"] = event.get_user_id()


@asmr_get.got("filename", prompt="请输入排除器/交换人")
async def handle_method(bot: Bot, event: Event, state: T_State):
    res = await get_txt(state["method"], state["filename"])
    res = "\n".join(str(i) for i in res)
    await asmr_get.finish(res)


# !筛选列表
asmr_filter = on_command("asmr筛选", rule=to_me(), priority=5)
asmr_compare = on_command("asmr对比", rule=to_me(), priority=5)


@asmr_compare.handle()
@asmr_filter.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["filter"] = args


@asmr_filter.got("filter", prompt="请输入需要排除器(以空格区分)")
async def handle_method(bot: Bot, event: Event, state: T_State):
    # 获取筛选器
    RJfilters = state["filter"].strip().split(" ")
    # 获取我自己的列表
    MyList = await get_txt("我的", event.get_user_id())
    # 使用筛选器
    [code, MyFilterList] = await get_RJlist(MyList, RJfilters)
    if code != 200:
        await asmr_filter.finish(f"{MyFilterList}")
    res = "\n".join(str(i) for i in MyFilterList)
    await asmr_filter.finish(f"筛选后的列表为\n{res}")


# !对比列表
@asmr_compare.got("filter", prompt="请输入需要的排除器(以空格区分)")
async def handle_method(bot: Bot, event: Event, state: T_State):
    pass


@asmr_compare.got("compare", prompt="请输入交换人")
async def handle_method(bot: Bot, event: Event, state: T_State):
    # 获取筛选器
    RJfilters = state["filter"].strip().split(" ")
    # 获取我自己的列表
    MyList = await get_txt("我的", event.get_user_id())
    # 获取交换人的列表
    HisList = await get_txt("交换", state["compare"].strip())
    if len(HisList) == 0:
        await asmr_filter.finish(f"交换人数据不存在")
    # 使用筛选器
    [code, MyFilterList] = await get_RJlist(MyList, RJfilters)
    if code != 200:
        await asmr_filter.finish(f"{MyFilterList}")
    [code, HisFilterList] = await get_RJlist(HisList, RJfilters)

    CommonList = [x for x in MyFilterList if x in HisFilterList]
    HisFilterList = [y for y in HisFilterList if y not in CommonList]
    MyFilterList = [y for y in MyFilterList if y not in CommonList]

    res = "\n".join(str(i) for i in HisFilterList)
    await asmr_filter.send(f"交换人独有列表为\n{res}")

    res = "\n".join(str(i) for i in MyFilterList)
    await asmr_filter.send(f"我独有列表为\n{res}")

    await asmr_filter.send(f"对比完成")

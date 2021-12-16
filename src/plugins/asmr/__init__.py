import re

from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.plugin import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State

from .config import Config
from .data_source import get_filepath, get_RJlist, get_RJlist_filter, write_RJlist

global_config = get_driver().config
config = Config(**global_config.dict())


asmr_add = on_command("asmr添加", rule=to_me(), priority=5)
asmr_get = on_command("asmr获取", rule=to_me(), priority=5)

# !添加列表
# *获取数据模式
@asmr_add.handle()
@asmr_get.handle()
async def handle_ag_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["method"] = args


# *获取数据模式
@asmr_add.got("method", prompt="请输入模式")
@asmr_get.got("method", prompt="请输入模式")
async def handle_ag_method(bot: Bot, event: Event, state: T_State):
    # *拆分模式参数,第一项为模式,其余项为参数
    method = state["method"].strip().split(" ")
    state["method"] = method
    # 从配置获取模式列表
    if method[0] not in config.methodList:
        await asmr_add.finish("不支持此方法")
    # !这里写死了,之后想办法重构
    if method[0] == "我的":
        state["filename"] = event.get_user_id()


# *获取文件名
@asmr_add.got("filename", prompt="请输入排除器/交换人")
async def handle_a_filename(bot: Bot, event: Event, state: T_State):
    pass


# *获取写入列表
@asmr_add.got("list", prompt="请输入列表")
async def handle_a_list(bot: Bot, event: Event, state: T_State):
    RJlist = state["list"]
    # 查找所有的RJ号
    RJlist = re.findall(r"(RJ\d{6})", RJlist)
    # 写入数据
    res = await write_RJlist(state["method"], state["filename"], RJlist)
    await asmr_add.finish(res)


# !获取列表
# *获取文件名
@asmr_get.got("filename", prompt="请输入排除器/交换人")
async def handle_g_filename(bot: Bot, event: Event, state: T_State):
    res = await get_RJlist(state["method"][0], state["filename"])
    if res == []:
        await asmr_get.finish("列表不存在")

    await bot.upload_group_file(
        group_id=event.group_id,
        name=f"{state['method'][0]}-{state['filename']}.txt",
        file=await get_filepath(state["method"][0], state["filename"]),
    )
    await asmr_get.finish(f"获取成功")


# !筛选列表
asmr_filter = on_command("asmr筛选", rule=to_me(), priority=5)
asmr_compare = on_command("asmr对比", rule=to_me(), priority=5)


@asmr_filter.handle()
@asmr_compare.handle()
async def handle_fc_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["filter"] = args


@asmr_filter.got("filter", prompt="请输入需要排除器(以空格区分)")
async def handle_f_filter(bot: Bot, event: Event, state: T_State):
    # 获取筛选器
    RJfilters = state["filter"].strip().split(" ")
    # 获取我自己的列表
    MyList = await get_RJlist("我的", event.get_user_id())
    # 使用筛选器
    [code, MyFilterList] = await get_RJlist_filter(MyList, RJfilters)
    # 判断状态
    if code != 200:
        await asmr_filter.finish(f"{MyFilterList}")

    # 返回列表
    res = "\n".join(str(i) for i in MyFilterList)
    await asmr_filter.finish(f"筛选后的列表为\n{res}")


# !对比列表
@asmr_compare.got("filter", prompt="请输入需要的排除器(以空格区分)")
async def handle_c_filter(bot: Bot, event: Event, state: T_State):
    pass


@asmr_compare.got("compare", prompt="请输入交换人")
async def handle_c_compare(bot: Bot, event: Event, state: T_State):
    # 获取筛选器
    RJfilters = state["filter"].strip().split(" ")
    # 获取我自己的列表
    MyList = await get_RJlist("我的", event.get_user_id())
    # 获取交换人的列表
    HisList = await get_RJlist("交换", state["compare"].strip())
    if len(HisList) == 0:
        await asmr_filter.finish(f"交换人数据不存在")

    # 使用筛选器
    [code, MyFilterList] = await get_RJlist_filter(MyList, RJfilters)
    if code != 200:
        await asmr_filter.finish(f"不支持此排除器 {MyFilterList}")
    [code, HisFilterList] = await get_RJlist_filter(HisList, RJfilters)

    CommonList = [x for x in MyFilterList if x in HisFilterList]
    HisFilterList = [y for y in HisFilterList if y not in CommonList]
    MyFilterList = [y for y in MyFilterList if y not in CommonList]

    # 写入临时文件并发送
    await write_RJlist(["临时", "-f"], "HisFilterList", ["列表获取时间"] + HisFilterList)
    await bot.upload_group_file(
        group_id=event.group_id,
        name="交换人独有列表.txt",
        file=await get_filepath("临时", "HisFilterList"),
    )

    await write_RJlist(["临时", "-f"], "MyFilterList", ["列表获取时间"] + MyFilterList)
    await bot.upload_group_file(
        group_id=event.group_id,
        name="我的独有列表.txt",
        file=await get_filepath("临时", "MyFilterList"),
    )

    await asmr_filter.send(f"对比完成")

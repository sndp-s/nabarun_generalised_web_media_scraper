import asyncio


async def main():
    q = asyncio.Queue()

    await q.put({"key": "value"})
    await q.put("2")
    await q.put("3")
    # q.task_done()


    print(await q.get())
    print(await q.get())
    print(await q.get())
    print(await q.get())


asyncio.run(main())

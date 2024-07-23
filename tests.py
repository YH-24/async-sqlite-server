from asyncio import run
from aiohttp import request

url = 'http://localhost:8080/new/database?router=player'

schema = ({'table': 'info', 'rows': ({'username': {'type': 'TEXT', 'value': 'Peanut butter shrimp'}})},)

router = 'player'

payload = {'router': router, 'schema': schema}


async def new_db():
    async with request(url=url, json=payload, method='POST') as req:
        return await req.read()


print(run(new_db()))

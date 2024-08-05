from asyncio import run
from aiohttp import request

url = 'http://localhost:8080/new/database?router=player'

rows_sa = ({'table': 'items', 'rows': (
    {
        'quantity': {'type': 'INT', 'value': 1},
        'name': {'type': 'TEXT', 'value': 'Peanut butter shrimp'},
        'rarity': {'type': 'INT', 'value': 1}

    },

)},
{'table': 'info', 'rows': (
    {
        'username': {'type': 'TEXT', 'value': 'The man'},
        'nickname': {'type': 'TEXT', 'value': 'blah blah'}
    },
)}
)

rows_c = ({'table': 'items', 'cols': ('name', 'quantity', 'rarity')})
# rows_v =

payload = {'rows': rows_sa, 'schema': 'player'}


async def new_db():
    async with request(url=f'{url}', json=payload, method='POST') as req:

        return await req.read()


print(run(new_db()))

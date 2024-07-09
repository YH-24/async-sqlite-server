# from sanic import Sanic, Request, response as Response
import asyncio
from uuid import uuid4
from structures import DatabaseManager, DatabaseFile, DatabaseTable, DatabaseRouter

loop = asyncio.new_event_loop()
# print(db.config_from_yaml())


async def main() -> 0:
    db = await DatabaseManager.create()
    players: DatabaseRouter = db.router['player']
    table: DatabaseTable = await players.get_table('data')

    await table.insert_row({'uuid': {'value': str(uuid4())}, 'username': {'value': 'aa'}})
    print(await table.get_rows(where={'uuid': 's'}))
    # print(table)


loop.create_task(main())
loop.run_forever()

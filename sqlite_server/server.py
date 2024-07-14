
from uuid import uuid4
from sqlite_server.structures import Server, DatabaseManager, DatabaseFile, DatabaseTable, DatabaseRouter, ServerMeth
from fastapi import FastAPI, Request, Response, Path

# print(db.config_from_yaml())
app = Server()
@app.route('/{path:path}')
async def index(req: Request,):
    # print(app.config)
    # return Response(content='blahh')
    return await app.meth.handle_req(req)

# players: DatabaseRouter = db.router['player']
# table: DatabaseTable = await players.get_table('data')

# await table.insert_row({'uuid': {'value': str(uuid4())}, 'username': {'value': 'aa'}})
# print(await table.get_rows(where={'uuid': 's'}))
# print(table)

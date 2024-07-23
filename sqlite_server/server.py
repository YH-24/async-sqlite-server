import os
from uuid import uuid4

from sqlite_server.exceptions import InvalidAPIPath
from sqlite_server.structures import ensure_conn, Server, DatabaseManager, DatabaseFile, DatabaseTable, DatabaseRouter, ServerMeth
from fastapi import FastAPI, Request, Response, Path

app = Server()


@app.get('/get/router/{router_name:str}/')
async def get_db(req: Request):
    search_key = req.query_params.get('key', None)
    search_value = req.query_params.get('value', None)

    router_name = req.path_params.get('router_name', None)

    if not router_name:
        raise InvalidAPIPath('missing router name in get/router endpoint')

    router = app.db.router.get(str(router_name).lower(), None)

    if not router:
        raise InvalidAPIPath(f'router "{router_name}" does not exist')

    if not search_key:
        raise InvalidAPIPath('router search key (?key=) not provided')
    # return Response(content=list(), media_type='application/json')

    return Response(str(await router.get_key({f"{search_key}": search_value})))


@app.get('/fetch/database/{db_id: str}/table/{table:str}')
async def get_table(req: Request):
    db_id = req.path_params.get('db_id', None)
    table_str = req.path_params.get('table', None)
    if not db_id or not table_str:
        raise InvalidAPIPath('database or table not provided')
    fp = f'./database/common/{db_id}.db'
    if not os.path.exists(fp):
        raise InvalidAPIPath(f'no database found at "{fp}"')
    db: DatabaseFile = await app.db.open_db(fp)
    table: DatabaseTable = await db.get_table(table_name=table_str)

    return table.refresh()


@app.post('/new/database')
async def create_db(req: Request):
    uuid_opt = req.query_params.get('uuid', uuid4())
    router_name = req.query_params.get('router', None)
    body = await req.json()

    schema = body.get('schema', {})
    items = body.get('rows', ())

    router: DatabaseRouter = app.db.router.get(str(router_name), None)

    if router:
        await router.add_key({'uuid': {'value': str(uuid_opt)}, 'username': {'value': 'bazingas'}})

    schema_dict = app.db.config['common'].get(str(schema), {})

    if isinstance(schema, dict):
        schema_dict = schema

    if isinstance(items, list):
        pass
    fp = f'./database/common/{uuid_opt}.db'
    db = await app.db.new_db(fp, schema=schema_dict)

    for item in items:
        for row in item['rows']:
            await db.tables[item['table']].insert_row(row)

        # db.tables[item['name']] = await DatabaseTable.create(db.conn, item['name'],)
        print(item)
    db.conn = await ensure_conn(fp, conn=db.conn)
    await db.conn.commit()
    return db.tables


@app.route('/{path:path}')
async def index(req: Request, ):
    return await app.meth.handle_req(req)

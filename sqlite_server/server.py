import os.path
from typing import Union
from uuid import uuid4
from sqlite_server.structures import Server, DatabaseManager, DatabaseFile, DatabaseTable, DatabaseRouter, ServerMeth
from fastapi import FastAPI, Request, Response, Path

app = Server()

@app.post('/database/{id:str}')
async def create_db(req: Request, schema: Union[dict, str] = None):

    db_id = req.path_params.get('id', None)
    config = app.db.config['meta']['database']

    if not db_id:
        return Response('No database id provided')
    print(f'./{config["base_path"]}{config["common_path"]}{db_id}.db')
    if os.path.exists(f'./{config["base_path"]}{config["common_path"]}{db_id}.db'):
        return Response('Database already exists')

    await app.db.new_db(db_id, schema=schema)
    return Response('Created database')


@app.get('/database/{id:str}/{table:str}')
async def get_db_from_router(req: Request, ):

    db_id = req.path_params.get('id', None)
    table = req.path_params.get('table', None)

    config = app.db.config['meta']['database']

    if not db_id:
        return Response('No database id provided')
    print(f'./{config["base_path"]}{config["common_path"]}{db_id}.db')
    if os.path.exists(f'./{config["base_path"]}{config["common_path"]}{db_id}.db'):
        print('db exists')

#
#     return Response('test')


@app.route('/{path:str}')
async def handle_all(req: Request,):
    return await app.meth.handle_req(req)

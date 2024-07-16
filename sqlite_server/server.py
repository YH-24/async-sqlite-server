
from uuid import uuid4
from sqlite_server.structures import Server, DatabaseManager, DatabaseFile, DatabaseTable, DatabaseRouter, ServerMeth
from fastapi import FastAPI, Request, Response, Path

app = Server()
@app.route('/{path:path}')
async def index(req: Request,):
    return await app.meth.handle_req(req)


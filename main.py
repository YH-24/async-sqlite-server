from sqlite_server.server import app
from asyncio import new_event_loop
from hypercorn.asyncio import serve
from hypercorn.config import Config

if __name__ == '__main__':
    loop = new_event_loop()

    print('Doing pre-init server setup..')
    loop.run_until_complete(app.pre_run())
    print('DB loaded successfully.')

    loop.run_until_complete(serve(app, Config.from_mapping({'bind': f'{app.config["host"]}:{app.config["port"]}'})))

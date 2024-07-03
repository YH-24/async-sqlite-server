from sanic import Sanic, Request, response as Response
from structures import DatabaseManager

db = DatabaseManager()

print(db.config_from_yaml())


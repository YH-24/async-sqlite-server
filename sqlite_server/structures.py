import os
import pathlib
from typing import Union, Iterable
from uuid import uuid4

import aiofiles as aiofiles
from aiosqlite import connect, Connection, Cursor
from yaml import parse, load
from yaml.loader import UnsafeLoader

from exceptions import MalformedSchema, DatabaseConnectionLost


def repeat(times: int, char='?', sep=', '):
    return sep.join(char for x in range(times))


async def ensure_conn(fp: str, conn: Connection = None):
    if conn:
        try:
            await (await conn.cursor()).close()
            return conn
        except:
            pass

    return await connect(fp).__aenter__()


class DatabaseRow:
    pass


class DatabaseTable:
    conn: Connection
    fp: str = None
    name: str
    schema: dict = {}
    rows: list = []

    def __init__(self, conn, name, fp: str = None, schema: dict = None, rows: list = None):
        self.conn = conn
        self.fp = fp
        self.name = name
        self.schema = schema if schema else {}
        self.rows = rows if rows else []

    def __repr__(self):
        return f'<DatabaseTable {self.name}, {self.rows} schema={self.schema}>'

    @classmethod
    async def create(cls, conn, name, cols, unique=False, fp: str = None):
        conn = await ensure_conn(fp, conn=conn)
        type_keys = [f'{col_name} {col["type"]}{" DEFAULT " + col["default"] if col.get("default", None) else ""}' for
                     col_name, col in cols.items()]
        await conn.execute(f'CREATE TABLE IF NOT EXISTS {name} ({", ".join(type_keys)})')
        if 'UNIQUE' in ''.join(type_keys):
            unique = True

        self = cls(conn, name, schema=cols, fp=fp)

        await self.insert_row(cols, unique=unique)

        await conn.commit()

        return self

    async def get_rows(self, cols: Union[list, str] = '*', where: dict = None, row_limit: int = 1, update: bool = False):
        cur: Cursor = await self.conn.cursor()

        if not where:
            where_str = ''
            where_params = tuple()
        else:
            where_params = where.values()
            where_str = ' WHERE ' + ', '.join([f"{key}=?" for key in where.keys()])
        await cur.execute(f'SELECT {cols} FROM {self.name}{where_str}', tuple(where_params))

        if row_limit == 1:
            rows = [await cur.fetchone()]
        elif row_limit == -1:
            rows = await cur.fetchall()
        else:
            rows = await cur.fetchmany(abs(int(row_limit)))
        await cur.close()
        col_rows = []

        for row in rows:
            if not row:
                continue
            for index, (col, data) in enumerate(self.schema[self.name].items()):
                if index < len(row):
                    col_rows.append({col: {'type': data['type'], 'value': data['value'] if not row else row[index]}})

        if update:
            self.rows = col_rows
        return col_rows

    async def insert_row(self, cols, unique: bool = True, or_: str = ''):

        self.conn = await ensure_conn(self.fp, conn=self.conn)

        # cur = await self.conn.cursor()

        values = {}
        has_defaults = False

        for col_name, col in cols.items():
            if col.get('value', None):
                values[col_name] = col['value']
            if not has_defaults:
                if col.get('default', None):
                    has_defaults = True

        if unique:
            or_ = 'OR IGNORE'

        values_str = ' DEFAULT VALUES '
        if values:
            values_str = f' ({", ".join(values.keys())}) VALUES ({repeat(len(values.keys()))})'

        self.conn = await ensure_conn(self.fp, conn=self.conn)
        await self.conn.execute(
            f'INSERT {or_} INTO {self.name}  {values_str}',
            tuple(values.values()))

        await self.conn.commit()


class DatabaseFile:
    conn: Connection
    fp: str
    tables: dict = {}
    schema: dict = {}

    def __init__(self, fp, conn, schema: dict = None, tables: dict = None):
        self.fp = fp
        self.conn = conn
        self.tables = tables if tables else {}
        self.schema = schema if schema else {}


    @classmethod
    async def create(cls, fp: str, schema: dict = None, persist: bool = False):
        tables = {}
        db_conn = await connect(fp).__aenter__()
        for table, cols in schema.items():
            tables[table] = await DatabaseTable.create(db_conn, table, cols, fp=fp)

        await db_conn.commit()

        if not persist:
            await db_conn.__aexit__(0, 0, 0)

        return cls(fp, db_conn, schema=schema)

    async def refresh(self, table):
        pass

    async def get_table(self, table_name, cols: Union[str, Iterable] = '*', row_limit: int = -1):
        if isinstance(cols, tuple) or isinstance(cols, list):
            cols = ', '.join(cols)

        self.conn = await ensure_conn(self.fp, conn=self.conn)
        table = DatabaseTable(self.conn, table_name, schema=self.schema, fp=self.fp)
        await table.get_rows(cols=cols, row_limit=row_limit, update=True)

        self.tables[table_name] = table
        return self.tables[table_name]


class DatabaseRouter(DatabaseFile):
    def __init__(self, fp, conn, router_table: str = 'data', schema: dict = None, tables: dict = None):
        super().__init__(fp=fp, conn=conn, schema=schema, tables=tables)

        self.router_table = router_table

    async def add_key(self, cols):
        if not self.tables.get(self.router_table, None):
            self.tables[self.router_table] = await self.get_table(self.router_table, cols=cols)

        uuid_taken = True
        uuid = uuid4()

        row = await self.tables[self.router_table].get_row(where={'uuid': uuid})

        while uuid_taken:
            if row:
                pass

    pass


class DatabaseManager:
    config: dict

    def __init__(self, config, routers):
        self.config = config
        self.router = routers
        pass

    @classmethod
    async def create(cls):
        config = await cls.config_from_yaml()
        routers = {}
        for name, router in config['router'].items():
            if not routers.get(name, None):
                routers[name] = await DatabaseRouter.create(f'../database/router/{name}.db', schema=router,
                                                            persist=True)

        return cls(config, routers)

    @staticmethod
    async def config_from_yaml(config_dir: str = '../config/'):
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(f'{config_dir}schemas/', exist_ok=True)

        config = {}

        if not os.path.exists(f'{config_dir}meta.yaml'):
            async with aiofiles.open('./meta.yaml', 'r') as meta_copy_raw:
                meta_data = await meta_copy_raw.read()

                async with aiofiles.open(f'{config_dir}meta.yaml', 'w') as meta_dest:
                    await meta_dest.write(meta_data)

        async with aiofiles.open(f'{config_dir}meta.yaml', 'r') as meta_raw:
            meta_parsed = load(await meta_raw.read(), UnsafeLoader)
            config['meta'] = meta_parsed
            config['router'] = {}
            config['common'] = {}

        for schema_name in os.listdir(f'{config_dir}schemas/'):
            schema_path = f'{config_dir}schemas/{schema_name}'
            async with aiofiles.open(schema_path) as schema_file:
                schema = load(await schema_file.read(), UnsafeLoader)

                if not schema:
                    raise MalformedSchema(f'Invalid schema file / missing all data {schema_path}')

                if not schema.get('schema_type', None):
                    raise MalformedSchema(f'Missing key "schema_type" in {schema_path}')
                schema_type = schema['schema_type']
                del schema['schema_type']
                for db_name, db in schema.items():
                    config[schema_type][db_name] = db

        return config

    print('pass gas')

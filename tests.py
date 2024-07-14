# def repeat(times: int, char='?', sep=', '):
#     return sep.join(char for x in range(times))
#
# print(repeat(2))
from fastapi import Response, Header

endpoints = {'/db': {'methods': ['OPTIONS'], '/router': {'/fetch': {'methods': ['GET']}, '/add': {'methods': ['POST']},
                                                         '/remove': {'methods': ['PUT', 'PATCH']}},
                     '/common': {'methods': ['GET', 'POST'], '/fetch_tables/': None,
                                 '/table/<database:str>/<table:str>': {'methods': ['PUT', 'PATCH']},
                                 '/query/<database:str>': {'auth': 'dev'}}}, '/auth': None}

special_keys = ('methods', 'response', 'auth')


def handle_response(res_input: dict, headers: dict = None):
    if not headers:
        headers = {'content-type': 'text/plain'}

    content = 'Endpoint is under construction...'

    if isinstance(res_input, dict):
        if res_input.get('response', None) and res_input['response'].get('content', None):
            content = str(res_input['response']['content']).format()

    return Response(content=content)


def iter_endpoints(data, parent_key='', functions=None):
    if functions is None:
        functions = {}

    for key, value in data.items():
        set_key = f'{parent_key}{key}'
        endpoint = {}

        if key in special_keys:  # current key is not parent but is either response, methods, or auth

            endpoint[key] = value

            set_key = parent_key

        elif isinstance(value, dict):
            iter_endpoints(value, parent_key=set_key, functions=functions)

        res = handle_response(endpoint.get('response', None))

        functions[set_key] = {'response': res, 'methods': endpoint.get('methods', ('GET',))}

    return functions

url_path = 'http://localhost:8080/foo/bar/baz'.split("/", 3)[3:]

print(url_path)
print('/' if not url_path else f'/{url_path[0]}')

def repeat(times: int, char='?', sep=', '):
    return sep.join(char for x in range(times))

print(repeat(2))
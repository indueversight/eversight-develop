import time
from functools import wraps
from time import time
import os
import shutil


def find_path(graph, start, path):
    path += [start]
    if start not in graph.keys():
        return path
    node = graph[start]
    if node in path:
        raise ValueError('Graph has a cycle')
    return find_path(graph, node, path)


def timeit(func):
    """
    :param func: Decorated function
    :return: Execution time for the decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print(f'>>{func.__name__} executed in {end - start:.2f} seconds')
        return result

    return wrapper


def copy_directory(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            pass
        else:
            shutil.copy2(s, d)

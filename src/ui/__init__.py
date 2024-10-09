import sys

def flush(func):
    def wrapper(x):
        sys.stdout.flush()
        return func(x)
    return wrapper

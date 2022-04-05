
cache = {0: 0, 1: 1}


def fib(n: int) -> []:
    """
    Return the nth Fibonacci number
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n in cache:
        return cache[n]
    else:
        cache[n] = fib(n - 1) + fib(n - 2)
        return cache[n]

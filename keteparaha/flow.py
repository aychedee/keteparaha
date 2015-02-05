def ignore(func, errors):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors:
            pass
    return wrapper


def retry(func, errors, attempts=5):
    def wrapper(*args, **kwargs):
        retries = attempts
        while retries:
            try:
                return func(*args, **kwargs)
            except errors:
                retries -= 1
        raise
    return wrapper


# -*- coding: utf-8 -*-
"""Flow control decorators

Example:
    from keteparaha import GmailImapClient
    from keteparaha.flow import retry

    gmail = GmailImapClient('test@email.com', 'xxxx')
    retryable_search = retry(gmail.gmail_search, Exception)
"""

def ignore(func, errors):
    """Ignore exceptions given in errors"""
    def wrapper(*args, **kwargs):
        """Wrapper func"""
        try:
            return func(*args, **kwargs)
        except errors:
            pass
    return wrapper


def retry(func, errors, attempts=5):
    """Retry the action if an exception occurs"""
    def wrapper(*args, **kwargs):
        """Wrapper func"""
        retries = attempts
        while retries:
            try:
                return func(*args, **kwargs)
            except errors:
                retries -= 1
        raise
    return wrapper

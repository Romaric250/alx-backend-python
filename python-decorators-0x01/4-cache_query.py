import time
import sqlite3
import functools

query_cache = {}



def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query') if 'query' in kwargs else args[1]
        if query in query_cache:
            print("Using cached result")
            return query_cache[query]
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)


users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)
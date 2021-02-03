import os
import psycopg2
import sqlalchemy
import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, Depends

# Router

router = APIRouter()


def fetch_query_records(query):
    """
    Creates a connection to database, returns query from specified table.
    Input: query: a SQL query (string)
    Returns: response: cursor.fetchall() object in array form
    """
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Creating Connection Object
    conn = psycopg2.connect(DATABASE_URL)
    # Creating Cursor Object
    cursor = conn.cursor()
    # Execute query
    cursor.execute(query)
    # Query results
    response = list(cursor.fetchall())
    # Closing Connection
    conn.close()

    return response


def fetch_query(query, columns):
    """
    Creates a connection to database, returns query from specified table
    as a list of dictionaries.
    Input: query: a SQL query (string)
    Returns: pairs: dataframe of cursor.fetchall() response in JSON pairs
    """
    # Fetch query
    response = fetch_query_records(query)
    # List of tuples to DF
    df = pd.DataFrame(response, columns=columns)
    # DF to dictionary
    pairs = df.to_json(orient='records')
    return pairs
async def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.
    
    Uses this environment variable if it exists:  
    DATABASE_URL=dialect://user:password@host/dbname

    Otherwise uses a SQLite database for initial local development.
    """
    load_dotenv()
    database_url = os.getenv('DATABASE_URL', default='sqlite:///temporary.db')
    engine = sqlalchemy.create_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@router.get('/info')
async def get_url(connection=Depends(get_db)):
    """Verify we can connect to the database, 
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """
    url_without_password = repr(connection.engine.url)
    return {'database_url': url_without_password}


# @router.get('/cityname')
# async def get_table(connection=Depends(get_db)):
#     """Return table of all data from CitySpire DB in json object"""
#     cursor = connection.cursor()
#     select_query = "SELECT * from citySpire"
#     cursor.execute(select_query)
#     records = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return json.dumps(records)

# def fetch_query(connection=Depends(get_db),query, columns):
#     """
#     Creates a connection to database, returns query from specified table
#     as a list of dictionaries.
#     Input: query: a SQL query (string)
#     Returns: pairs: dataframe of cursor.fetchall() response in JSON pairs
#     """
#     # Creating Cursor Object
#     cursor = connection.cursor()
#     # Execute query
#     cursor.execute(query)
#     # Query results
#     response = list(cursor.fetchall())
#     # Fetch query
#     response = fetch_query_records(query)
#     # List of tuples to DF
#     df = pd.DataFrame(response, columns=columns)
#     # DF to dictionary
#     pairs = df.to_json(orient='records')
#     return pairs
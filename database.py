import os
import aiomysql

# MySQL connection parameters
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'sqlflamegraph')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))

async def get_connection():
    """Get an async MySQL connection"""
    return await aiomysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        port=MYSQL_PORT,
        autocommit=True
    )

async def save_explain(explain_output, ip_address=None, user_agent=None):
    """Save EXPLAIN data to the database asynchronously"""
    conn = await get_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO explains (explain_output, ip_address, user_agent, created_at)
                VALUES (%s, %s, %s, NOW())
                """,
                (explain_output, ip_address, user_agent)
            )
            return cursor.lastrowid
    except Exception as e:
        print(f"Error saving explain: {str(e)}")
        raise
    finally:
        conn.close()
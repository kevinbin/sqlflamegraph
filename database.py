import asyncpg
import asyncio

# PostgreSQL connection string
DB_URL = "postgres://koyeb-adm:npg_0YvdLErITM8p@ep-fancy-sky-a2xtigpt.eu-central-1.pg.koyeb.app/sqlflamegraph"

async def get_connection():
    """Get an async PostgreSQL connection"""
    return await asyncpg.connect(DB_URL)

async def save_explain(explain_output, ip_address=None, user_agent=None):
    """Save EXPLAIN data to the database asynchronously"""
    conn = await get_connection()
    try:
        record_id = await conn.fetchval(
            """
            INSERT INTO explain (explain_output, ip_address, user_agent)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            explain_output, ip_address, user_agent
        )
        return record_id
    except Exception as e:
        print(f"Error saving explain: {str(e)}")
        raise
    finally:
        await conn.close()
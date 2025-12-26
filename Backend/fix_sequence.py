"""
Fix PostgreSQL sequence for users table
"""
import asyncio
import asyncpg
from app.config import settings

async def fix_sequence():
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DATABASE
    )
    
    try:
        # Fix users sequence
        result = await conn.fetchval(
            "SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1))"
        )
        print(f"✅ Users sequence fixed. Next value will be: {result + 1}")
        
        # Also fix other sequences if needed
        tables = ['chats', 'chat_messages', 'progress', 'exercises', 'exercise_completions', 
                  'reflections', 'topics', 'knowledge_items', 'techniques']
        
        for table in tables:
            try:
                result = await conn.fetchval(
                    f"SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )
                print(f"✅ {table} sequence fixed. Next value: {result + 1}")
            except Exception as e:
                print(f"⚠️ Could not fix {table} sequence: {e}")
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_sequence())

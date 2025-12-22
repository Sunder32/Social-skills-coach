
import asyncio
from sqlalchemy import text
from app.database import engine


async def migrate_database():
    print("=" * 60)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    async with engine.begin() as conn:

        print("\n1. Проверка структуры таблицы users...")
        
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN reset_token VARCHAR(500)"
            ))
            print("   ✅ Добавлено поле reset_token")
        except Exception as e:
            print(f"   ⚠️  Поле reset_token уже существует или ошибка: {e}")
        
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN reset_token_expires DATETIME"
            ))
            print("   ✅ Добавлено поле reset_token_expires")
        except Exception as e:
            print(f"   ⚠️  Поле reset_token_expires уже существует или ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("МИГРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate_database())

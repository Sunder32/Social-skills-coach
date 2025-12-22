import asyncio
from sqlalchemy import text
from app.database import engine


async def migrate_database():
    print("=" * 60)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ - ПОДТВЕРЖДЕНИЕ EMAIL")
    print("=" * 60)
    
    async with engine.begin() as conn:
        print("\nДобавление полей для подтверждения email...")
        
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN verification_code VARCHAR(10)"
            ))
            print("   ✅ Добавлено поле verification_code")
        except Exception as e:
            print(f"   ⚠️  Поле verification_code уже существует или ошибка: {e}")
        
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN verification_code_expires DATETIME"
            ))
            print("   ✅ Добавлено поле verification_code_expires")
        except Exception as e:
            print(f"   ⚠️  Поле verification_code_expires уже существует или ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("МИГРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate_database())

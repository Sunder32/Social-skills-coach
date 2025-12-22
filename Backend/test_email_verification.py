import asyncio
from app.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserCreate


async def test_email_verification():
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПОДТВЕРЖДЕНИЯ EMAIL")
    print("=" * 80)
    
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        
        test_email = "verify.test@example.com"
        test_password = "testpass123"
        
        print("\n1. Создание пользователя...")
        existing = await service.get_by_email(test_email)
        if existing:
            print(f"   ⚠️  Пользователь уже существует")
            await session.delete(existing)
            await session.commit()
            print(f"   🗑️  Старый пользователь удалён")
        
        user_data = UserCreate(
            email=test_email,
            password=test_password,
            name="Тест Подтверждения"
        )
        
        user = await service.create(user_data)
        print(f"   ✅ Создан пользователь: {user.name} ({user.email})")
        print(f"      is_verified: {user.is_verified}")
        print(f"      verification_code: {user.verification_code}")
        
        verification_code = user.verification_code
        
        print("\n2. Попытка входа БЕЗ подтверждения email...")
        try:
            auth_user = await service.authenticate(test_email, test_password)
            print(f"   ❌ Вход разрешён БЕЗ подтверждения (ошибка!)")
        except Exception as e:
            print(f"   ✅ Правильно отклонено: {e}")
        
        print("\n3. Подтверждение email с неверным кодом...")
        try:
            await service.verify_email(test_email, "000000")
            print(f"   ❌ Неверный код принят (ошибка!)")
        except Exception as e:
            print(f"   ✅ Правильно отклонено: {e}")
        
        print("\n4. Подтверждение email с правильным кодом...")
        try:
            result = await service.verify_email(test_email, verification_code)
            if result:
                print(f"   ✅ Email успешно подтверждён")
                
                await session.refresh(user)
                print(f"      is_verified: {user.is_verified}")
                print(f"      verification_code: {user.verification_code}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n5. Попытка входа ПОСЛЕ подтверждения email...")
        try:
            auth_user = await service.authenticate(test_email, test_password)
            if auth_user:
                print(f"   ✅ Успешный вход")
                print(f"      Пользователь: {auth_user.name}")
                print(f"      Подтверждён: {auth_user.is_verified}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n6. Попытка повторного подтверждения...")
        try:
            await service.verify_email(test_email, "123456")
            print(f"   ❌ Повторное подтверждение прошло (ошибка!)")
        except Exception as e:
            print(f"   ✅ Правильно отклонено: {e}")
        
        print("\n7. Тест повторной отправки кода...")
        
        print("   Создание нового неподтверждённого пользователя...")
        test_email2 = "resend.test@example.com"
        existing2 = await service.get_by_email(test_email2)
        if existing2:
            await session.delete(existing2)
            await session.commit()
        
        user_data2 = UserCreate(
            email=test_email2,
            password=test_password,
            name="Тест Повторной Отправки"
        )
        
        user2 = await service.create(user_data2)
        old_code = user2.verification_code
        print(f"   Старый код: {old_code}")
        
        print("   Запрос повторной отправки...")
        await service.resend_verification_code(test_email2)
        
        await session.refresh(user2)
        new_code = user2.verification_code
        print(f"   Новый код: {new_code}")
        
        if old_code != new_code:
            print(f"   ✅ Код успешно обновлён")
        else:
            print(f"   ⚠️  Код не изменился")
    
    print("\n" + "=" * 80)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 80)
    print("\n📧 ПРИМЕЧАНИЕ:")
    print("   - Проверьте логи сервера для просмотра писем с кодами")
    print("   - В режиме разработки письма не отправляются реально")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_email_verification())

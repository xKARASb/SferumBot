"""Интерактивная аутентификация PyMax с вводом кода подтверждения"""

import asyncio
import logging
from typing import Optional
from pymax import MaxClient

logger = logging.getLogger(__name__)

class PyMaxAuth:
    """Класс для интерактивной аутентификации PyMax"""
    
    def __init__(self, phone: str, work_dir: str = "cache"):
        """
        Инициализация аутентификации
        
        Args:
            phone: Телефонный номер в международном формате
            work_dir: Директория для хранения сессии
        """
        self.phone = phone
        self.work_dir = work_dir
        self.client: Optional[MaxClient] = None
        
    async def authenticate_interactive(self) -> bool:
        """
        Интерактивная аутентификация с вводом кода подтверждения
        
        Returns:
            bool: Успешность аутентификации
        """
        try:
            print(f"🔐 Начинаем аутентификацию PyMax для номера: {self.phone}")
            print("📱 На ваш телефон должен прийти код подтверждения из приложения Макс")
            
            # Инициализация клиента
            self.client = MaxClient(phone=self.phone, work_dir=self.work_dir)
            
            # Попытка запуска клиента
            try:
                await self.client.start()
                print("✅ Аутентификация прошла успешно!")
                return True
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "code" in error_msg or "confirmation" in error_msg or "verify" in error_msg:
                    # Запрашиваем код подтверждения
                    code = await self._request_confirmation_code()
                    if code:
                        # Повторная попытка с кодом
                        try:
                            await self.client.start(code=code)
                            print("✅ Аутентификация с кодом прошла успешно!")
                            return True
                        except Exception as retry_error:
                            print(f"❌ Ошибка при вводе кода: {retry_error}")
                            return False
                    else:
                        print("❌ Код не был введен")
                        return False
                else:
                    print(f"❌ Ошибка аутентификации: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Критическая ошибка при аутентификации: {e}")
            return False
    
    async def _request_confirmation_code(self) -> Optional[str]:
        """
        Запрос кода подтверждения у пользователя
        
        Returns:
            Optional[str]: Введенный код или None если отмена
        """
        print("\n" + "="*50)
        print("🔐 ТРЕБУЕТСЯ КОД ПОДТВЕРЖДЕНИЯ")
        print("="*50)
        print("1. Откройте приложение Макс на вашем телефоне")
        print("2. Найдите уведомление о входе с нового устройства")
        print("3. Скопируйте код подтверждения")
        print("4. Введите его ниже")
        print("-"*50)
        
        # Интерактивный ввод кода
        for attempt in range(3):  # 3 попытки ввода
            try:
                if attempt == 0:
                    code = input("🔑 Введите код подтверждения: ").strip()
                else:
                    code = input(f"🔑 Попытка {attempt + 1}/3. Введите код: ").strip()
                
                if not code:
                    print("❌ Код не может быть пустым")
                    continue
                    
                if code.lower() in ['cancel', 'exit', 'quit']:
                    print("❌ Аутентификация отменена")
                    return None
                    
                # Проверка формата кода (обычно 4-6 цифр)
                if code.isdigit() and 4 <= len(code) <= 6:
                    return code
                else:
                    print("⚠️ Код должен состоять из 4-6 цифр")
                    
            except KeyboardInterrupt:
                print("\n❌ Аутентификация прервана")
                return None
            except Exception as e:
                print(f"❌ Ошибка ввода: {e}")
                
        print("❌ Превышено количество попыток ввода кода")
        return None
    
    async def test_connection(self) -> bool:
        """
        Тестирование соединения после аутентификации
        
        Returns:
            bool: Успешность теста
        """
        if not self.client:
            print("❌ Клиент не инициализирован")
            return False
            
        try:
            # Получаем список чатов для проверки
            chats = self.client.chats
            print(f"✅ Соединение установлено! Найдено чатов: {len(chats)}")
            
            # Показываем первые несколько чатов
            for i, chat in enumerate(chats[:5]):
                chat_title = getattr(chat, 'title', f'Chat {chat.id}')
                print(f"   {i+1}. {chat_title} (ID: {chat.id})")
                
            if len(chats) > 5:
                print(f"   ... и еще {len(chats) - 5} чатов")
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка тестирования соединения: {e}")
            return False
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            try:
                await self.client.close()
                print("✅ Клиент PyMax закрыт")
            except Exception as e:
                print(f"⚠️ Ошибка закрытия клиента: {e}")


async def setup_max_interactive(phone: str) -> bool:
    """
    Основная функция для интерактивной настройки PyMax
    
    Args:
        phone: Телефонный номер
        
    Returns:
        bool: Успешность настройки
    """
    print("🚀 НАСТРОЙКА PYMAX АУТЕНТИФИКАЦИИ")
    print("="*50)
    
    auth = PyMaxAuth(phone)
    
    try:
        # Интерактивная аутентификация
        if await auth.authenticate_interactive():
            print("\n🔍 Проверяем соединение...")
            if await auth.test_connection():
                print("\n✅ PyMax успешно настроен и готов к работе!")
                print("💾 Сессия сохранена в директории 'cache'")
                print("🔄 Последующие запуски будут использовать сохраненную сессию")
                return True
            else:
                print("\n❌ Не удалось проверить соединение")
                return False
        else:
            print("\n❌ Не удалось пройти аутентификацию")
            return False
            
    finally:
        await auth.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Использование: python pymax_auth.py +79123456789")
        sys.exit(1)
        
    phone = sys.argv[1]
    
    # Проверка формата телефона
    if not phone.startswith('+') or not phone[1:].isdigit():
        print("❌ Неверный формат телефона. Используйте международный формат: +79123456789")
        sys.exit(1)
    
    # Запуск интерактивной аутентификации
    success = asyncio.run(setup_max_interactive(phone))
    sys.exit(0 if success else 1)
import redis
from typing import Optional, Any
from app.config import settings

class RedisClient:
    """Менеджер подключения и операций Redis"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    def ping(self) -> bool:
        """Проверка подключения к Redis"""
        try:
            return self.client.ping()
        except Exception as e:
            print(f"Ошибка подключения Redis: {e}")
            return False
    
    def set_value(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Установить значение в Redis с опциональным TTL"""
        try:
            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            print(f"Ошибка установки значения: {e}")
            return False
    
    def get_value(self, key: str) -> Optional[str]:
        """Получить значение из Redis"""
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Ошибка получения значения: {e}")
            return None
    
    def increment(self, key: str) -> Optional[int]:
        """Увеличить счётчик в Redis"""
        try:
            return self.client.incr(key)
        except Exception as e:
            print(f"Ошибка инкремента: {e}")
            return None
    
    def delete_key(self, key: str) -> bool:
        """Удалить ключ из Redis"""
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            return False
    
    def get_all_keys(self) -> list:
        """Получить все ключи из Redis"""
        try:
            keys = self.client.keys("*")
            return keys if keys else []
        except Exception as e:
            print(f"Ошибка получения ключей: {e}")
            return []

# Создаём singleton экземпляр
redis_client = RedisClient()
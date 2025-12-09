import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.redis_client import redis_client

client = TestClient(app)

class TestHealthCheck:
    def test_health_check(self):
        """Тест эндпоинта проверки здоровья"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "application" in data
        assert "redis" in data

class TestSetValue:
    def test_set_value_success(self):
        """Тест установки значения в Redis"""
        response = client.post("/set", json={
            "key": "test_key",
            "value": "test_value"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["key"] == "test_key"
        assert data["value"] == "test_value"
    
    def test_set_value_with_ttl(self):
        """Тест установки значения с TTL"""
        response = client.post("/set", json={
            "key": "ttl_key",
            "value": "ttl_value",
            "ttl": 3600
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_set_value_missing_key(self):
        """Тест установки значения без ключа"""
        response = client.post("/set", json={
            "key": "",
            "value": "test_value"
        })
        assert response.status_code == 400

class TestGetValue:
    def test_get_value_success(self):
        """Тест получения значения из Redis"""
        # Сначала установим значение
        client.post("/set", json={
            "key": "get_test_key",
            "value": "get_test_value"
        })
        
        # Затем получим его
        response = client.get("/get?key=get_test_key")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["key"] == "get_test_key"
        assert data["value"] == "get_test_value"
    
    def test_get_nonexistent_key(self):
        """Тест получения несуществующего ключа"""
        response = client.get("/get?key=nonexistent_key_12345")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"

class TestIncrement:
    def test_increment_new_key(self):
        """Тест инкремента нового счётчика"""
        response = client.post("/incr", json={
            "key": "counter_key"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["value"] == 1
    
    def test_increment_existing_key(self):
        """Тест инкремента существующего счётчика"""
        # Установим начальное значение
        client.post("/set", json={
            "key": "counter_key_2",
            "value": "5"
        })
        
        # Увеличиваем его
        response = client.post("/incr", json={
            "key": "counter_key_2"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["value"] == 6

class TestDelete:
    def test_delete_existing_key(self):
        """Тест удаления существующего ключа"""
        # Сначала установим значение
        client.post("/set", json={
            "key": "delete_test_key",
            "value": "delete_test_value"
        })
        
        # Затем удалим его
        response = client.post("/delete", json={
            "key": "delete_test_key"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_delete_nonexistent_key(self):
        """Тест удаления несуществующего ключа"""
        response = client.post("/delete", json={
            "key": "nonexistent_delete_key"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"

class TestGetAllKeys:
    def test_get_all_keys(self):
        """Тест получения всех ключей"""
        response = client.get("/keys")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "keys" in data
        assert isinstance(data["keys"], list)

class TestHomePage:
    def test_home_page(self):
        """Тест главной страницы"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Redis" in response.text
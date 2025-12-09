from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from app.config import settings
from app.redis_client import redis_client

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI приложение с интеграцией Redis"
)

# Модели
class KeyValue(BaseModel):
    key: str
    value: str
    ttl: Optional[int] = None

class KeyRequest(BaseModel):
    key: str

class CounterRequest(BaseModel):
    key: str

# Проверка здоровья при запуске
@app.on_event("startup")
async def startup_event():
    """Проверить подключение Redis при запуске"""
    if not redis_client.ping():
        print("ПРЕДУПРЕЖДЕНИЕ: Не удалось подключиться к Redis")

# Маршрут 1: Главная страница
@app.get("/", response_class=HTMLResponse)
async def home():
    """Главная страница с описанием проекта"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Redis Веб Приложение</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 900px;
                width: 100%;
                padding: 40px;
            }
            
            h1 {
                color: #333;
                margin-bottom: 20px;
                text-align: center;
                font-size: 2.5em;
            }
            
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            
            .endpoint-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-decoration: none;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .endpoint-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
            
            .endpoint-card h3 {
                margin-bottom: 10px;
                font-size: 1.2em;
            }
            
            .endpoint-card p {
                font-size: 0.9em;
                line-height: 1.6;
            }
            
            .features {
                background: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
                border-left: 4px solid #667eea;
            }
            
            .features h3 {
                color: #333;
                margin-bottom: 15px;
            }
            
            .features ul {
                list-style: none;
                padding-left: 0;
            }
            
            .features li {
                padding: 8px 0;
                color: #555;
                padding-left: 25px;
                position: relative;
            }
            
            .features li:before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: bold;
            }
            
            .swagger-link {
                display: inline-block;
                margin-top: 20px;
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                transition: background 0.3s;
                text-align: center;
                margin-right: 10px;
            }
            
            .swagger-link:hover {
                background: #764ba2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Redis Веб-приложение</h1>
            <p class="subtitle">FastAPI + Redis Интеграция</p>
            
            <div class="endpoints">
                <div class="endpoint-card">
                    <h3>📝 POST /set</h3>
                    <p>Установить значение в Redis с опциональным TTL</p>
                </div>
                <div class="endpoint-card">
                    <h3>📖 GET /get</h3>
                    <p>Получить значение по ключу из Redis</p>
                </div>
                <div class="endpoint-card">
                    <h3>⬆️ POST /incr</h3>
                    <p>Увеличить счётчик в Redis</p>
                </div>
                <div class="endpoint-card">
                    <h3>🗑️ POST /delete</h3>
                    <p>Удалить ключ из Redis</p>
                </div>
            </div>
            
            <div class="features">
                <h3>Особенности:</h3>
                <ul>
                    <li>REST API с FastAPI фреймворком</li>
                    <li>Интеграция Redis для хранения данных</li>
                    <li>Конфигурация через переменные окружения</li>
                    <li>Контейнеризация с Docker</li>
                    <li>Оркестрация с Docker Compose</li>
                    <li>GitHub Actions CI/CD пайплайн</li>
                </ul>
            </div>
            
            <a href="/docs" class="swagger-link">📚 API Документация (Swagger UI)</a>
            <a href="/redoc" class="swagger-link">📖 API Документация (ReDoc)</a>
        </div>
    </body>
    </html>
    """
    return html_content

# Маршрут 2: Установить значение
@app.post("/set")
async def set_value(data: KeyValue):
    """
    Установить значение в Redis
    
    Пример:
    {
        "key": "username",
        "value": "john_doe",
        "ttl": 3600
    }
    """
    if not data.key or not data.value:
        raise HTTPException(status_code=400, detail="Ключ и значение обязательны")
    
    try:
        success = redis_client.set_value(data.key, data.value, data.ttl)
        if success:
            return {
                "status": "success",
                "message": f"Значение установлено для ключа '{data.key}'",
                "key": data.key,
                "value": data.value,
                "ttl": data.ttl or "Без истечения"
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка установки значения")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Маршрут 3: Получить значение
@app.get("/get")
async def get_value(key: str = Query(..., description="Ключ для получения")):
    """
    Получить значение из Redis по ключу
    
    Пример: /get?key=username
    """
    if not key:
        raise HTTPException(status_code=400, detail="Ключ обязателен")
    
    try:
        value = redis_client.get_value(key)
        if value is not None:
            return {
                "status": "success",
                "key": key,
                "value": value
            }
        else:
            return {
                "status": "not_found",
                "key": key,
                "message": f"Ключ '{key}' не найден в Redis"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Маршрут 4: Увеличить счётчик
@app.post("/incr")
async def increment(data: CounterRequest):
    """
    Увеличить счётчик в Redis
    
    Пример:
    {
        "key": "page_views"
    }
    """
    if not data.key:
        raise HTTPException(status_code=400, detail="Ключ обязателен")
    
    try:
        new_value = redis_client.increment(data.key)
        if new_value is not None:
            return {
                "status": "success",
                "key": data.key,
                "value": new_value,
                "message": f"Счётчик '{data.key}' увеличен до {new_value}"
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка инкремента")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Маршрут 5: Удалить ключ
@app.post("/delete")
async def delete_key(data: KeyRequest):
    """
    Удалить ключ из Redis
    
    Пример:
    {
        "key": "username"
    }
    """
    if not data.key:
        raise HTTPException(status_code=400, detail="Ключ обязателен")
    
    try:
        success = redis_client.delete_key(data.key)
        if success:
            return {
                "status": "success",
                "message": f"Ключ '{data.key}' удален",
                "key": data.key
            }
        else:
            return {
                "status": "not_found",
                "message": f"Ключ '{data.key}' не найден",
                "key": data.key
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Дополнительный маршрут: Получить все ключи
@app.get("/keys")
async def get_all_keys():
    """Получить все ключи, хранящиеся в Redis"""
    try:
        keys = redis_client.get_all_keys()
        return {
            "status": "success",
            "count": len(keys),
            "keys": keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Проверка здоровья приложения
@app.get("/health")
async def health_check():
    """Проверить здоровье приложения и Redis"""
    redis_healthy = redis_client.ping()
    return {
        "status": "healthy" if redis_healthy else "unhealthy",
        "application": "running",
        "redis": "connected" if redis_healthy else "disconnected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
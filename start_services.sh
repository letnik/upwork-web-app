#!/bin/bash

# Скрипт для запуску всіх сервісів Upwork AI Assistant

echo "🚀 Запуск сервісів Upwork AI Assistant..."

# Зупиняємо існуючі процеси
echo "🛑 Зупиняємо існуючі процеси..."
pkill -f "uvicorn.*auth-service" || true
pkill -f "uvicorn.*upwork-service" || true
pkill -f "uvicorn.*ai-service" || true
pkill -f "uvicorn.*analytics-service" || true
pkill -f "uvicorn.*notification-service" || true

sleep 2

# Запускаємо сервіси в фоновому режимі
echo "🔧 Запускаємо Auth Service (порт 8001)..."
cd app/backend/services/auth-service
uvicorn src.main:app --host 0.0.0.0 --port 8001 > /tmp/auth-service.log 2>&1 &
AUTH_PID=$!

echo "🔧 Запускаємо Upwork Service (порт 8002)..."
cd ../upwork-service
uvicorn src.main:app --host 0.0.0.0 --port 8002 > /tmp/upwork-service.log 2>&1 &
UPWORK_PID=$!

echo "🔧 Запускаємо AI Service (порт 8003)..."
cd ../ai-service
uvicorn src.main:app --host 0.0.0.0 --port 8003 > /tmp/ai-service.log 2>&1 &
AI_PID=$!

echo "🔧 Запускаємо Analytics Service (порт 8004)..."
cd ../analytics-service
uvicorn src.main:app --host 0.0.0.0 --port 8004 > /tmp/analytics-service.log 2>&1 &
ANALYTICS_PID=$!

echo "🔧 Запускаємо Notification Service (порт 8005)..."
cd ../notification-service
uvicorn src.main:app --host 0.0.0.0 --port 8005 > /tmp/notification-service.log 2>&1 &
NOTIFICATION_PID=$!

# Повертаємося в корінь проекту
cd ../../../

echo "⏳ Чекаємо запуску сервісів..."
sleep 5

# Перевіряємо статус сервісів
echo "📊 Перевіряємо статус сервісів..."

echo "✅ Auth Service:"
curl -s "http://localhost:8001/" | jq '.' 2>/dev/null || echo "❌ Не працює"

echo "✅ Upwork Service:"
curl -s "http://localhost:8002/" | jq '.' 2>/dev/null || echo "❌ Не працює"

echo "✅ AI Service:"
curl -s "http://localhost:8003/" | jq '.' 2>/dev/null || echo "❌ Не працює"

echo "✅ Analytics Service:"
curl -s "http://localhost:8004/" | jq '.' 2>/dev/null || echo "❌ Не працює"

echo "✅ Notification Service:"
curl -s "http://localhost:8005/" | jq '.' 2>/dev/null || echo "❌ Не працює"

echo ""
echo "🎉 Сервіси запущені!"
echo "📝 Логи:"
echo "   Auth Service: tail -f /tmp/auth-service.log"
echo "   Upwork Service: tail -f /tmp/upwork-service.log"
echo "   AI Service: tail -f /tmp/ai-service.log"
echo "   Analytics Service: tail -f /tmp/analytics-service.log"
echo "   Notification Service: tail -f /tmp/notification-service.log"
echo ""
echo "🔗 Endpoints:"
echo "   Auth Service: http://localhost:8001"
echo "   Upwork Service: http://localhost:8002"
echo "   AI Service: http://localhost:8003"
echo "   Analytics Service: http://localhost:8004"
echo "   Notification Service: http://localhost:8005"
echo ""
echo "🧪 Тестування OAuth:"
echo "   curl http://localhost:8001/auth/oauth/upwork/test" 
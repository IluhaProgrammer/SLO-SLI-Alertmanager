# Учебный проект по Prometheus / Grafana / Alertmanager, посвящённый **recording rules**, **SLI / SLO** и **SLO-based алертингу**.

Проект демонстрирует, как из сырых метрик приложения получить **понятные показатели надёжности сервиса** (availability, error rate) и использовать их для мониторинга и алертов.

## 🎯 Цели проекта

- Понять, **зачем нужны recording rules**
- Научиться оптимизировать тяжёлые PromQL-запросы
- Разобраться в терминах **SLI / SLO / SLA**
- Реализовать:
  - Availability SLI
  - Error Rate
- Настроить **SLO-based alerts**
- Собрать полноценный monitoring stack в Docker Compose


## 🧱 Архитектура

```
┌──────────┐
│ FastAPI │
│ /metrics │
└────┬─────┘
│
┌────▼─────┐
│Prometheus│
│ - scrape │
│ - rules │
│ - alerts │
└────┬─────┘
│
┌────▼─────┐ ┌────────────┐
│ Grafana │ │Alertmanager│
│ Dashboards│◄──────│ SLO alerts │
└──────────┘ └────────────┘
```


## 🛠️ Используемый стек

- **FastAPI** — тестовое приложение
- **prometheus_client** — экспорт метрик
- **Prometheus** — сбор и обработка метрик
- **Recording Rules** — предагрегация метрик
- **Grafana** — визуализация SLI
- **Alertmanager** — алерты по SLO
- **Docker / Docker Compose**

## 📊 Метрики приложения

Экспортируются следующие метрики:

- `http_requests_total{method, path, status}`
- `http_request_duration_seconds`

Эндпоинты:
- `/` — успешный запрос (200)
- `/error` — ошибка (500)
- `/metrics` — Prometheus metrics

## 📈 Recording Rules

Recording rules используются для:
- снижения нагрузки на Prometheus
- упрощения PromQL-запросов
- переиспользования метрик в Grafana и Alertmanager

### Реализованные recording rules:

- **Общий RPS**
- **Успешные запросы**
- **Ошибочные запросы**
- **Availability SLI**
- **Error Rate**

Примеры:

```
app:availability:ratio5m

app:error_rate:ratio5m
```

## 📐 SLI / SLO

### SLI (Service Level Indicators)

- **Availability**
    
- **Error Rate**
    

### SLO (Service Level Objectives)

- Availability ≥ **99.9%**
    
- Error Rate ≤ **0.1%**
    

SLO используется как основа для алертинга.

## 🚨 Алерты

Реализован SLO-based alert:

- **HighErrorRate**
    
    - Срабатывает, если error rate > 0.1%
        
    - Окно: 5 минут
        
    - Использует recording rules, а не сырые метрики


Alert rules:
```
groups:
- name: slo.alerts
  rules:
  - alert: HighErrorRate
    expr: app:error_rate:rate5m > 0.001
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate"
      description: "Error rate > 0.1% for 2 minutes"
```

Recording rules:
```
groups:
- name: app.rules
  rules:
  - record: app:http_requests:rate5m
    expr: sum(rate(http_requests_total[5m]))

  - record: app:http_requests:success:rate5m
    expr: sum(rate(http_requests_total{status=~"2..|3.."}[5m]))
  
  - record: app:http_requests:error:rate5m
    expr: sum(rate(http_requests_total{status=~"5.."}[5m]))
    
  - record: app:availability:rate5m
    expr: app:http_requests:success:rate5m
          /
          app:http_requests:rate5m

  - record: app:error_rate:rate5m
    expr: app:http_requests:error:rate5m
          /
          app:http_requests:rate5m
```

Alertmanager config:
```
global:
  resolve_timeout: 5m


route:
  receiver: telegram
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - matchers:
      - severity="critical"
      receiver: telegram


receivers:
  - name: telegram
    telegram_configs:
      - bot_token: secret
        chat_id: secret
        parse_mode: HTML
```
## 🚀 Запуск проекта

`docker compose up -d --build`

## 🔍 Проверка сервисов

- FastAPI: http://localhost:8000
    
- Prometheus: http://localhost:9090
    
- Grafana: http://localhost:3000
    
- Alertmanager: http://localhost:9093
    

Grafana:

- login: `admin`
    
- password: `admin`
    


## 🔥 Генерация нагрузки

```
for i in {1..100}; do curl http://localhost:8000/; done 
for i in {1..10}; do curl http://localhost:8000/error; done
```

#### Grafana dashboard во время нагрузки:

<img width="696" height="487" alt="image" src="https://github.com/user-attachments/assets/aed0b465-910f-4026-9750-489de3bd3b96" />

#### Alert в телегу:

<img width="443" height="185" alt="image" src="https://github.com/user-attachments/assets/bf49fd71-9b0c-44dc-b975-141c2d39cf1b" />

## 📊 Примеры PromQL для Grafana

**Availability (%)**

`app:availability:ratio5m * 100`

**Error Rate (%)**

`app:error_rate:ratio5m * 100`

## Grafana dashboard 

<img width="693" height="450" alt="image" src="https://github.com/user-attachments/assets/33f4c8c3-ceaa-4ae8-be19-65546fbcbb0f" />

## 🧠 Результат

В рамках проекта:

- ✔ реализованы recording rules
    
- ✔ рассчитаны SLI
    
- ✔ заданы SLO
    
- ✔ настроены SLO-based alerts
    
- ✔ собран production-like monitoring stack
    

Проект демонстрирует подход к мониторингу, ориентированный не на инфраструктурные метрики, а на **надёжность сервиса**.

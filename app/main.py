from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest
import random
import time


app = FastAPI()


REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)


LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["path"]
)


@app.get("/")
def root():
    with LATENCY.labels("/").time():
        time.sleep(random.uniform(0.05, 0.2))
        status = "200"
        REQUESTS.labels("GET", "/", status).inc()
        return {"status": "ok"}


@app.get("/error")
def error():
    with LATENCY.labels("/error").time():
        time.sleep(random.uniform(0.05, 0.2))
        status = "500"
        REQUESTS.labels("GET", "/error", status).inc()
        return Response(status_code=500)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
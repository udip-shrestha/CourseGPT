import time
from fastapi import Request, Response
from fastapi.routing import APIRoute
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

# API metrics
request_count = Counter(
    'http_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY,
)
request_duration = Histogram(
    'http_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY,
)

# Discord metrics
discord_command_count = Counter(
    'discord_commands_total',
    'Total Discord bot commands',
    ['command', 'outcome'],
    registry=REGISTRY,
)
discord_command_duration = Histogram(
    'discord_command_duration_seconds',
    'Duration of Discord bot commands',
    ['command', 'outcome'],
    registry=REGISTRY,
)

class MetricsRoute(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request):
            # avoid recording the metrics endpoint itself
            if request.url.path == "/metrics":
                return await original_handler(request)

            method = request.method
            endpoint = self.path  # route template like /courses/{course_id}
            start = time.time()

            response = await original_handler(request)

            status = str(response.status_code)
            duration = time.time() - start

            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint, status=status).observe(duration)

            return response

        return custom_handler

def metrics_response():
    return Response(generate_latest(REGISTRY), media_type="text/plain")
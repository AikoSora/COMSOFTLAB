from django.urls import path

from .consumers import EmailConsumer


websocket_urlpatterns = [
    path('emails/', EmailConsumer.as_asgi()),
]


__all__ = (
    'websocket_urlpatterns',
)

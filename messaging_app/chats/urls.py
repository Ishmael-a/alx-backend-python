from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversations")
router.register("messages", MessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]

# urlpatterns = router.urls

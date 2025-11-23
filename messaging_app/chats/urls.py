from django.urls import path, include
from rest_framework import routers as drf_routers
from .views import ConversationViewSet, MessageViewSet
from rest_framework_nested import routers

router = drf_routers.DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversations")
router.register("messages", MessageViewSet, basename="messages")

conversation_router = routers.NestedSimpleRouter(router, "conversations", lookup="conversation")
conversation_router.register("messages", MessageViewSet, basename="conversation-messages")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(conversation_router.urls)),
]

# urlpatterns = router.urls

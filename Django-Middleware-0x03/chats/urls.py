from django.urls import path, include
from rest_framework import routers as drf_routers
from .views import ConversationViewSet, MessageViewSet
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView
from chats.auth import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ChangePasswordView
)

router = drf_routers.DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversations")
router.register("messages", MessageViewSet, basename="messages")

# conversation_router = routers.NestedSimpleRouter(router, "conversations", lookup="conversation")
# conversation_router.register("messages", MessageViewSet, basename="conversation-messages")


urlpatterns = [
    path("", include(router.urls)),
    # path("", include(conversation_router.urls)),

    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]

# urlpatterns = router.urls

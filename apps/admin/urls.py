from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import SimpleRouter
from admin.views.homeview import HomeView

from admin.views import user_login_view

urlpatterns = [
    # url(r'^authorizations/$', user_login_view.UserLoginView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]

router = SimpleRouter()
router.register(prefix='statistical', viewset=HomeView, base_name='home')
urlpatterns += router.urls
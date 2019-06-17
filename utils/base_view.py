from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class Base_view(LoginRequiredMixin, View):
    pass
from django.conf.urls import url
from evaluation.views import FrontAutomate

urlpatterns = [
    url(r'^code', FrontAutomate.as_view())
]

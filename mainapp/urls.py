from django.urls import path
from .views import MyUploadView, Graph,ShowFileColumns,CreateDateModel
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("upload/", MyUploadView.as_view()),
    path("graph/", Graph.as_view()),
    path("showfile/", ShowFileColumns.as_view()),
    path("learnmodel/", CreateDateModel.as_view()),
    # path("showgraph/", GraphView.as_view()),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


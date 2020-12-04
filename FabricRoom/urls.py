from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('main.urls'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('blog/', include('blog.urls')),
    path('health/', include('healthstats.urls'))
]

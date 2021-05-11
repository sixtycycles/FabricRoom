from django.contrib import admin
from django.urls import path, include
from main.views import custom_error_403, custom_error_404, custom_error_500

urlpatterns = [
    path('', include('main.urls'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('blog/', include('blog.urls')),
    path('health/', include('healthstats.urls'))
]

handler403 = 'main.views.custom_error_403'
handler404 = 'main.views.custom_error_404'
handler500 = 'main.views.custom_error_500'
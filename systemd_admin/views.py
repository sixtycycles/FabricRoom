import subprocess
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse

class SystemdDashboardView(PermissionRequiredMixin):
    permission_required = 'systemd_admin.can_view_systemd'
    template_name = 'systemd_admin/dashboard.html'
    raise_exception = True  # Returns a 403 Forbidden instead of redirecting to login

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # SAFE: Passing a hardcoded list of arguments, shell=False by default.
        # Never use shell=True or pass unsanitized user strings here.
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'list-units', '--type=service', '--state=active', '--no-legend'],
                capture_output=True, 
                text=True, 
                check=True
            )
            services = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(maxsplit=4)
                    if len(parts) >= 4:
                        services.append({
                            'name': parts[0],
                            'load': parts[1],
                            'active': parts[2],
                            'sub': parts[3],
                            'description': parts[4] if len(parts) > 4 else ''
                        })
            context['services'] = services
        except subprocess.CalledProcessError as e:
            context['error'] = f"Failed to fetch systemd data: {e.stderr}"
        
        return context
from django.conf import settings

def common(request):
    return {'GOOGLE_ANALYTICS_ACCOUNT': getattr(settings, 'GOOGLE_ANALYTICS_ACCOUNT', '')}


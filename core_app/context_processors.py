from .models import Market


def _session_location(request):
    return {
        'current_city': request.session.get('current_city', ''),
        'current_region': request.session.get('current_region', ''),
        'current_country': request.session.get('current_country', ''),
        'current_latitude': request.session.get('current_latitude'),
        'current_longitude': request.session.get('current_longitude'),
    }


def global_ui_context(request):
    markets = Market.objects.filter(active=True)[:6]
    location = _session_location(request)
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        location = {
            'current_city': profile.current_city or location['current_city'],
            'current_region': profile.current_region or location['current_region'],
            'current_country': profile.current_country or location['current_country'],
            'current_latitude': profile.current_latitude or location['current_latitude'],
            'current_longitude': profile.current_longitude or location['current_longitude'],
        }
    return {'global_markets': markets, **location}

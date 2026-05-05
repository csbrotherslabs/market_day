from .models import Market


def global_ui_context(request):
    markets = Market.objects.filter(active=True)[:6]
    return {'global_markets': markets}

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from core_app.decorators import role_required


TEMPLATE_PREVIEWS = {
    'fresh_simple': {
        'name': 'Fresh & Simple',
        'store_name': 'Ama Fresh Foods',
        'tagline': 'Farm Fresh Goodness',
        'subtag': 'Direct from our farm to your family',
        'theme_class': 'preview-fresh',
        'sections': ['categories', 'products', 'store_info'],
    },
    'boutique': {
        'name': 'Boutique',
        'store_name': 'Spice Haven',
        'tagline': 'Authentic African Spices',
        'subtag': 'Bold flavors. Rich traditions.',
        'theme_class': 'preview-boutique',
        'sections': ['categories', 'products', 'about', 'contact'],
    },
    'story_impact': {
        'name': 'Story & Impact',
        'store_name': 'The Green Basket',
        'tagline': 'Good Food. Healthy Living.',
        'subtag': 'Local produce for a brighter tomorrow.',
        'theme_class': 'preview-story',
        'sections': ['categories', 'products', 'about', 'impact'],
    },
    'modern_market': {
        'name': 'Modern Market',
        'store_name': "Kofi's Market",
        'tagline': 'Quality Produce. Local Prices.',
        'subtag': 'Fresh, local, trusted.',
        'theme_class': 'preview-modern',
        'sections': ['promotion', 'categories', 'products', 'featured'],
    },
    'premium_showcase': {
        'name': 'Premium Showcase',
        'store_name': 'Golden Harvest',
        'tagline': 'Excellence in Every Harvest',
        'subtag': 'Premium local produce for your table.',
        'theme_class': 'preview-premium',
        'sections': ['collection', 'products', 'quality', 'about', 'reviews'],
    },
    'creative_unique': {
        'name': 'Creative & Unique',
        'store_name': 'Market Vibes',
        'tagline': 'Good Food. Good People.',
        'subtag': 'Local markets. Stronger community.',
        'theme_class': 'preview-creative',
        'sections': ['gallery', 'products', 'about', 'community', 'contact'],
    },
}


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def store_template_preview(request, template_key):
    preview = TEMPLATE_PREVIEWS.get(template_key)
    if not preview:
        raise Http404('Store template not found.')

    products = [
        {'name': 'Fresh Tomatoes', 'price': '12.00', 'unit': 'kg', 'emoji': '🍅'},
        {'name': 'Garden Eggs', 'price': '10.00', 'unit': 'kg', 'emoji': '🍆'},
        {'name': 'Fresh Pepper', 'price': '15.00', 'unit': 'kg', 'emoji': '🌶️'},
        {'name': 'Red Onions', 'price': '12.00', 'unit': 'kg', 'emoji': '🧅'},
        {'name': 'Plantain', 'price': '8.00', 'unit': 'kg', 'emoji': '🍌'},
        {'name': 'Fresh Ginger', 'price': '25.00', 'unit': 'kg', 'emoji': '🫚'},
    ]
    categories = ['Fresh Vegetables', 'Fresh Fruits', 'Herbs & Spices', 'Grains & Beans']

    dedicated_templates = {
        'boutique': 'sellers_app/store_template_preview_boutique.html',
        'story_impact': 'sellers_app/store_template_preview_story_impact.html',
        'modern_market': 'sellers_app/store_template_preview_modern_market.html',
        'premium_showcase': 'sellers_app/store_template_preview_premium_showcase.html',
        'creative_unique': 'sellers_app/store_template_preview_creative_unique.html',
    }
    template_name = dedicated_templates.get(template_key, 'sellers_app/store_template_preview.html')

    return render(request, template_name, {
        'template_key': template_key,
        'preview': preview,
        'products': products,
        'categories': categories,
    })

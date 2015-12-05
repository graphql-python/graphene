from django.conf import settings

GRAPHENE_ORDER_BY_FIELD = getattr(settings, 'GRAPHENE_ORDER_BY_FIELD', 'order_by')
GRAPHENE_ENABLE_FILTERING = getattr(settings, 'GRAPHENE_ENABLE_FILTERING', False)

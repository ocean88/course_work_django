from django.core.cache import cache
from config.settings import CACHE_ENABLED


def get_model_from_cache(model):
    """Gets data from cache for the specified model, or retrieves from the database if cache is empty."""
    if not CACHE_ENABLED:
        return model.objects.all()

    key = f'{model.__name__.lower()}_list'  # Generate a unique cache key for the model
    data = cache.get(key)  # Attempt to retrieve data from cache
    if data is None:
        data = model.objects.all()
        cache.set(key, data)
    return data

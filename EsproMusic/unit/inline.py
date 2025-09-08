import re
from cachetools import TTLCache
from EsproMusic.core.mongo import mongodb

# MongoDB collections
user_collection = mongodb.user_collection
collection = mongodb.collection

# Caching to reduce database queries
all_characters_cache = TTLCache(maxsize=10000, ttl=300)   # 5 minutes
user_collection_cache = TTLCache(maxsize=10000, ttl=30)   # 30 seconds


async def get_user_collection(user_id: int):
    """Get user collection from database with cache"""
    user_id_str = str(user_id)
    if user_id_str in user_collection_cache:
        return user_collection_cache[user_id_str]

    user = await user_collection.find_one({'id': int(user_id)})
    if user:
        user_collection_cache[user_id_str] = user
    return user


async def search_characters(query: str, force_refresh: bool = False):
    """Search characters by name, anime, or aliases"""
    cache_key = f"search_{query.lower()}"
    if not force_refresh and cache_key in all_characters_cache:
        return all_characters_cache[cache_key]

    regex = re.compile(query, re.IGNORECASE)
    characters = await collection.find({
        "$or": [
            {"name": regex},
            {"anime": regex},
            {"aliases": regex}
        ]
    }).to_list(length=None)

    all_characters_cache[cache_key] = characters
    return characters


async def get_all_characters(force_refresh: bool = False):
    """Get all characters from database with optional cache refresh"""
    if not force_refresh and 'all_characters' in all_characters_cache:
        return all_characters_cache['all_characters']

    characters = await collection.find({}).to_list(length=None)
    all_characters_cache['all_characters'] = characters
    return characters


async def refresh_character_caches():
    """Clear all caches for fresh reload"""
    all_characters_cache.clear()
    user_collection_cache.clear()
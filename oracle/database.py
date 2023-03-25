import redis

database = redis.Redis()
database.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
database.get("Bahamas")
database.save()

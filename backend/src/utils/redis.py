import redis
import os

redis_host = os.getenv("REDIS_HOST", "localhost")

redis_client = redis.StrictRedis(
    host=redis_host,
    port=6379,
    db=2,  # 可以選一個專門用來存 prediction 的 DB
    decode_responses=True,  # 回傳字串
)

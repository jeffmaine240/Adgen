from src.config import Config
from redis import asyncio as aioredis # type: ignore

JTI_EXPIRY = 3600

redis = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
)


async def set_token_in_blacklist(token_jti: str) -> None:
    await redis.set(
        ex=JTI_EXPIRY,
        name=token_jti,
        value="",
    )

async def token_in_blacklist(token_jti: str) -> bool:
    token = await redis.get(name=token_jti)
    print(token)
    if token is not None:
        return True
    return False

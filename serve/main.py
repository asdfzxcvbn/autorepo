from time import perf_counter

import orjson
from fastapi import FastAPI, Response  # type: ignore

from ..filelock import FileLock


class OJResp(Response):
    media_type: str = "application/json"

    def render(self, content):
        return orjson.dumps(content)


app: FastAPI = FastAPI(default_response_class=OJResp)
last_time: float = perf_counter()
with FileLock("repo.json") as f:
    cache: dict = orjson.loads(f.read())


@app.get("/")
async def get_repo() -> dict:
    global cache, last_time
    if last_time + 120 < perf_counter():
        last_time = perf_counter()
        with FileLock("repo.json") as f:
            cache = orjson.loads(f.read())

    return cache

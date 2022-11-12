from src.containers import Container
from sanic.request import Request
from sanic.response import HTTPResponse


async def container_start(request: Request) -> None:
    request.ctx.container = Container()
    await request.ctx.container.init_resources()  # type: ignore


async def container_finish(request: Request, response: HTTPResponse) -> None:
    await request.ctx.container.shutdown_resources()

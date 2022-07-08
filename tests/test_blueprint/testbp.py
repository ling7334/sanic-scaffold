from sanic import Blueprint, HTTPResponse, Request, text

TestBP = Blueprint("test")


@TestBP.route("/")
async def test(request: Request) -> HTTPResponse:
    return text("ok")

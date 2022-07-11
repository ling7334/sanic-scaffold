from sanic import Blueprint, HTTPResponse, Request, json

from services.health import health

HealthBP = Blueprint("health")


@HealthBP.route("/")
async def health_endpoint(request: Request) -> HTTPResponse:
    """health endpoint

    Provides health information about the service.

    such as the version of the service, the version of the dependencies, connections etc.

    openapi:
    ---
    operationId: health
    tags:
      - health
    responses:
      '200':
        description: Health information about the service
    """
    return json(await health(request))

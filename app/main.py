import logging.config

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from app.config.settings import Settings
from app.api.endpoint.api import router
from app.log.logging_conf import get_logging_config

__version__ = "0.0.1"
logging.config.dictConfig(get_logging_config(settings=Settings()))


def create_app() -> FastAPI:
    settings = Settings()
    application = FastAPI(title="app", debug=settings.debug_mode, version=__version__)
    application.include_router(router)
    application.add_middleware(
        CorrelationIdMiddleware,
        header_name="Request-ID",
    )
    return application


app = create_app()


@app.on_event("startup")
async def startup_event():
    logging.info(f"Application version: {__version__}")
    logging.info("Application Ready!")


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down")

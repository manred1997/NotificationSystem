import os
import logging
from functools import partial

from typing import Optional, Text, Union, List, Tuple

import asyncio

import server
from server import create_ssl_context
from utils.utils import (
    configure_file_logging,
    list_routes,
    enable_async_loop_debugging,
    number_of_sanic_workers,
    update_sanic_log_level
    )
from utils.constants import (
    DEFAULT_SERVER_INTERFACE,
    DEFAULT_SERVER_PORT,
    DEFAULT_RESPONSE_TIMEOUT,
    ENV_SANIC_BACKLOG,
    HOST_LOCATE,
    TIME_ZONE,
    TIME_OUT,
    GEOGRAPHY,
    PROXIES,
    RETRIES,
    BACKOFF_FACTOR,
    REQUEST_ARGS
)
from agent import Agent

from sanic import Sanic


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def configure_app(
    cors: Optional[Union[Text, List[Text], None]] = None,
    auth_token: Optional[Text] = None,
    response_timeout: int = DEFAULT_RESPONSE_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    log_file: Optional[Text] = None,
) -> Sanic:
    """Run the agent."""
    configure_file_logging(logger, log_file)

    app = server.create_app(
        cors_origins=cors,
        auth_token=auth_token,
        response_timeout=response_timeout,
        jwt_secret=jwt_secret,
        jwt_method=jwt_method,
    )

    if logger.isEnabledFor(logging.DEBUG):
        list_routes(app)

    async def configure_async_logging() -> None:
        if logger.isEnabledFor(logging.DEBUG):
            enable_async_loop_debugging(asyncio.get_event_loop())

    app.add_task(configure_async_logging)
    return app

def serve_application(
    hl=HOST_LOCATE,
    tz=TIME_ZONE,
    geo=GEOGRAPHY,
    timeout=TIME_OUT,
    proxies=PROXIES,
    retries=RETRIES,
    backoff_factor=BACKOFF_FACTOR,
    requests_args=REQUEST_ARGS,
    interface: Optional[Text] = DEFAULT_SERVER_INTERFACE,
    port: int = DEFAULT_SERVER_PORT,
    cors: Optional[Union[Text, List[Text]]] = None,
    auth_token: Optional[Text] = None,
    response_timeout: int = DEFAULT_RESPONSE_TIMEOUT,
    log_file: Optional[Text] = None,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    ssl_certificate: Optional[Text] = None,
    ssl_keyfile: Optional[Text] = None,
    ssl_ca_file: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
    use_syslog: Optional[bool] = False,
    syslog_address: Optional[Text] = None,
    syslog_port: Optional[int] = None,
    syslog_protocol: Optional[Text] = None,
    ):

    app = configure_app(
        cors,
        auth_token,
        response_timeout,
        jwt_secret,
        jwt_method,
        log_file
    )

    ssl_context = create_ssl_context(
        ssl_certificate, ssl_keyfile, ssl_ca_file, ssl_password
    )
    protocol = "https" if ssl_context else "http"

    logger.info(f"Starting Knowlife server on {protocol}://{interface}:{port}")

    app.register_listener(
        partial(load_agent_on_start,
                hl,
                tz,
                geo,
                timeout,
                proxies,
                retries,
                backoff_factor,
                requests_args),
        "before_server_start",
    )

    number_of_workers = number_of_sanic_workers()
    update_sanic_log_level(
        log_file, use_syslog,
        syslog_address,
        syslog_port,
        syslog_protocol
    )
    app.run(
        host=interface,
        port=port,
        ssl=ssl_context,
        backlog=int(os.environ.get(ENV_SANIC_BACKLOG, "100")),
        workers=number_of_workers,
    )


def load_agent_on_start(
                    hl: Text,
                    tz: int,
                    geo: Text,
                    timeout: Tuple,
                    proxies: Text,
                    retries: int,
                    backoff_factor: int,
                    requests_args,
                    app: Sanic,
                    loop: Text,
    ) -> Agent:
    """Load an agent.
    Used to be scheduled on server start
    (hence the `app` and `loop` arguments)."""
    app.agent = Agent.load_agent(
        hl=hl,
        tz=tz,
        geo=geo,
        timeout=timeout,
        proxies=proxies,
        retries=retries,
        backoff_factor=backoff_factor,
        requests_args=requests_args,
    )
    if not app.agent:
        logger.warning(
            "Agent could not be loaded with the provided configuration. "
            "Load default agent without any model."
        )
        app.agent = Agent.load_agent(
            hl=HOST_LOCATE,
            tz=TIME_ZONE,
            geo=GEOGRAPHY,
            timeout=TIME_OUT,
            proxies=PROXIES,
            retries=RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            requests_args=REQUEST_ARGS,
        )

    return app.agent

if __name__ == '__main__':
    serve_application()
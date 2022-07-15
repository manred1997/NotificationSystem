import logging
import traceback
from typing import List, Optional, Text, Union, Any, Callable
from functools import wraps

from http import HTTPStatus

from sanic import Sanic, response
from sanic.request import Request
from sanic_cors import CORS
from sanic_jwt import Initialize, exceptions

from agent import Agent
from utils import DEFAULT_RESPONSE_TIMEOUT

logger = logging.getLogger(__name__)

class ErrorResponse(Exception):
    """Common exception to handle failing API requests."""

    def __init__(
        self,
        status: Union[int, HTTPStatus],
        reason: Text,
        message: Text,
        details: Any = None,
        help_url: Optional[Text] = None,
    ) -> None:
        """Creates error.
        Args:
            status: The HTTP status code to return.
            reason: Short summary of the error.
            message: Detailed explanation of the error.
            details: Additional details which describe the error. Must be serializable.
            help_url: URL where users can get further help (e.g. docs).
        """
        self.error_info = {
            "status": "failure",
            "message": message,
            "reason": reason,
            "details": details or {},
            "help": help_url,
            "code": status,
        }
        self.status = status
        logger.error(message)
        super(ErrorResponse, self).__init__()


def ensure_loaded_agent(
    app: Sanic, require_core_is_ready: bool = False
) -> Callable[[Callable], Callable[..., Any]]:
    """Wraps a request handler ensuring there is a loaded and usable agent.
    Require the agent to have a loaded Core model if `require_core_is_ready` is
    `True`.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            # noinspection PyUnresolvedReferences
            if not app.agent or not app.agent.is_ready():
                raise ErrorResponse(
                    HTTPStatus.CONFLICT,
                    "Conflict",
                    "No agent loaded. To continue processing, a "
                    "model of a trained agent needs to be loaded.",
                )

            return f(*args, **kwargs)

        return decorated

    return decorator

def create_ssl_context(
    ssl_certificate: Optional[Text],
    ssl_keyfile: Optional[Text],
    ssl_ca_file: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
) -> Optional["SSLContext"]:
    """Create an SSL context if a proper certificate is passed.
    Args:
        ssl_certificate: path to the SSL client certificate
        ssl_keyfile: path to the SSL key file
        ssl_ca_file: path to the SSL CA file for verification (optional)
        ssl_password: SSL private key password (optional)
    Returns:
        SSL context if a valid certificate chain can be loaded, `None` otherwise.
    """

    if ssl_certificate:
        import ssl

        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cafile=ssl_ca_file
        )
        ssl_context.load_cert_chain(
            ssl_certificate, keyfile=ssl_keyfile, password=ssl_password
        )
        return ssl_context
    else:
        return None

def configure_cors(
    app: Sanic, cors_origins: Union[Text, List[Text], None] = ""
) -> None:
    """Configure CORS origins for the given app."""

    # Workaround so that socketio works with requests from other origins.
    # https://github.com/miguelgrinberg/python-socketio/issues/205#issuecomment-493769183
    app.config.CORS_AUTOMATIC_OPTIONS = True
    app.config.CORS_SUPPORTS_CREDENTIALS = True

    CORS(
        app, resources={r"/*": {"origins": cors_origins or ""}}, automatic_options=True
    )

def validate_request_body(request: Request, error_message: Text):
    """Check if `request` has a body."""
    if not request.body:
        raise ErrorResponse(400, "BadRequest", error_message)

async def authenticate(request: Request):
    """Callback for authentication failed."""
    raise exceptions.AuthenticationFailed(
        "Direct JWT authentication not supported. You should already have "
        "a valid JWT from an authentication provider, Rasa will just make "
        "sure that the token is valid, but not issue new tokens."
    )

def create_app(
    agent: Optional["Agent"] = None,
    cors_origins: Union[Text, List[Text], None] = "*",
    auth_token: Optional[Text] = None,
    response_timeout: int = DEFAULT_RESPONSE_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Text = "HS256",
    ):
    app = Sanic(__name__)
    app.config.RESPONSE_TIMEOUT = response_timeout
    configure_cors(app, cors_origins)

    # Setup the Sanic-JWT extension
    if jwt_secret and jwt_method:
        # since we only want to check signatures, we don't actually care
        # about the JWT method and set the passed secret as either symmetric
        # or asymmetric key. jwt lib will choose the right one based on method
        app.config["USE_JWT"] = True
        Initialize(
            app,
            secret=jwt_secret,
            authenticate=authenticate,
            algorithm=jwt_method,
            user_id="username",
        )

    app.agent = agent

    @app.exception(ErrorResponse)
    async def handle_error_response(request: Request, exception: ErrorResponse):
        return response.json(exception.error_info, status=exception.status)
    
    @app.get("/health")
    @ensure_loaded_agent(app)
    def status(request: Request):
        """Determine if the container is working and healthy. In this sample container, we declare
        it healthy if we can load the model successfully."""

        return response.text('OK')

    @app.get("/get_trend_article")
    @ensure_loaded_agent(app)
    async def get_trend_article(request: Request):
        try:
            response_data = await app.agent.realtime_trending_searches()
            return response.json(response_data)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                500,
                "SearchingError",
                f"An unexpected error occurred during searching. Error: {e}",
            )
    
    return app

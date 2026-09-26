import logging
from logging.handlers import RotatingFileHandler

from app.db import DATA_DIR

LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return  # already set up (e.g. --reload restarting the app)

    LOG_DIR.mkdir(exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    # Attached to root so any of this app's own `logging.getLogger(__name__)`
    # calls land here. WARNING, not INFO: at INFO, third-party libraries with
    # chatty loggers (httpx, the openai SDK's HTTP client) inherit the root
    # level too and fill the file with routine request lines, rotating out
    # the actual errors this exists to capture.
    root.addHandler(handler)
    root.setLevel(logging.WARNING)

    # Also attached directly to the "uvicorn" logger: uvicorn's own logging
    # config (uvicorn.config.LOGGING_CONFIG) sets propagate=False on
    # "uvicorn" itself, which stops an unhandled-exception traceback logged
    # through the child logger "uvicorn.error" from ever reaching root's
    # handlers — propagation up the logger tree halts at the first ancestor
    # with propagate=False, regardless of "uvicorn.error"'s own propagate
    # flag. Attaching here, where that walk actually stops, is what makes
    # those tracebacks show up in the file instead of only live console
    # output. ("uvicorn.access", the per-request line, has its own
    # propagate=False and stops before even reaching "uvicorn", so it's
    # unaffected by this — deliberately, per-request noise is not wanted
    # here.)
    logging.getLogger("uvicorn").addHandler(handler)

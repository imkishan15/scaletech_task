import logging
import json
import time
import os

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "requests.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "request_logger": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING)
request_logger = logging.getLogger("request_logger")


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        log_data = {
            "request_method": request.method,
            "request_path": request.path,
            "request_body": (
                request.body.decode("utf-8", errors="ignore") if request.body else None
            ),
        }
        request_logger.debug(f"Request: {json.dumps(log_data)}")
        return None

    def process_response(self, request, response):
        total_time = time.time() - request.start_time
        log_data = {
            "request_method": request.method,
            "request_path": request.path,
            "response_status_code": response.status_code,
            "response_body": self.get_response_body(response),
            "response_time": f"{total_time:.4f}s",
        }
        request_logger.debug(f"Response: {json.dumps(log_data)}")
        return response

    def process_exception(self, request, exception):
        total_time = time.time() - request.start_time
        log_data = {
            "request_method": request.method,
            "request_path": request.path,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "response_time": f"{total_time:.4f}s",
        }
        request_logger.error(f"Exception: {json.dumps(log_data)}")
        return HttpResponse("An error occurred.", status=500)

    def get_response_body(self, response):
        try:
            if hasattr(response, "streaming_content"):
                return "Streaming Content"
            elif isinstance(response, HttpResponse) and response.content:
                return response.content.decode("utf-8", errors="ignore")
            else:
                return None
        except Exception as e:
            request_logger.error(f"Error decoding response body: {e}")
            return "Error decoding response"

import json
import os
import time

from langchain.tools import tool
from zai import ZhipuAiClient

from deerflow.config import get_app_config

SUPPORTED_FILE_TYPES = {
    "PDF", "DOCX", "DOC", "XLS", "XLSX", "PPT", "PPTX",
    "PNG", "JPG", "JPEG", "CSV", "TXT", "MD", "HTML",
}

USER_DATA_ROOT = "/mnt/user-data"

WEB_FETCH_MAX_CHARS = 4096
FILE_PARSER_MAX_CHARS = 16384


class PathAccessError(ValueError):
    """Raised when a file path is outside the allowed USER_DATA_ROOT."""


def _open_validated(file_path: str):
    """Open file then validate the opened fd is under USER_DATA_ROOT.

    Uses /proc/self/fd to resolve the real path from the open file descriptor,
    avoiding TOCTOU races. Linux-only — not portable to macOS/BSD.
    """
    f = open(file_path, "rb")
    try:
        real = os.path.realpath(f"/proc/self/fd/{f.fileno()}")
        if not real.startswith(USER_DATA_ROOT + os.sep) and real != USER_DATA_ROOT:
            raise PathAccessError(f"Access denied: {file_path} is outside {USER_DATA_ROOT}")
    except Exception:
        f.close()
        raise
    return f


def _get_bigmodel_client(tool_name: str = "web_search", config=None) -> ZhipuAiClient:
    if config is None:
        config = get_app_config().get_tool_config(tool_name)
    api_key = None
    if config is not None:
        api_key = config.model_extra.get("api_key")
    if not api_key and tool_name != "web_search":
        fallback = get_app_config().get_tool_config("web_search")
        if fallback is not None:
            api_key = fallback.model_extra.get("api_key")
    if not api_key:
        raise ValueError(
            f"No api_key configured for bigmodel tool '{tool_name}' or 'web_search' fallback"
        )
    return ZhipuAiClient(api_key=api_key)


def _tool_error(tool_name: str, detail: object) -> str:
    return json.dumps({"error": f"{tool_name} failed", "detail": str(detail)})


@tool("web_search", parse_docstring=True)
def web_search_tool(query: str) -> str:
    """Search the web.

    Args:
        query: The query to search for.
    """
    config = get_app_config().get_tool_config("web_search")
    extra = config.model_extra if config else {}
    max_results = extra.get("max_results", 5)
    search_engine = extra.get("search_engine", "search_pro")

    try:
        client = _get_bigmodel_client(config=config)
        response = client.web_search.web_search(
            search_engine=search_engine,
            search_query=query,
            search_intent=False,
            count=max_results,
        )
    except Exception as e:
        return _tool_error("web_search", e)

    search_result = getattr(response, "search_result", None)
    if search_result is None:
        return json.dumps({"error": "web_search API call failed", "detail": str(response)})
    results = search_result if isinstance(search_result, list) else [search_result]
    normalized = [
        {
            "title": getattr(r, "title", ""),
            "url": getattr(r, "link", ""),
            "snippet": getattr(r, "content", ""),
        }
        for r in results
    ]
    return json.dumps(normalized, indent=2, ensure_ascii=False)


@tool("web_fetch", parse_docstring=True)
def web_fetch_tool(url: str) -> str:
    """Fetch the contents of a web page at a given URL.
    Only fetch EXACT URLs that have been provided directly by the user or
    have been returned in results from the web_search and web_fetch tools.
    Do not guess or construct URLs.

    Args:
        url: The URL to fetch the contents of.
    """
    config = get_app_config().get_tool_config("web_fetch")
    extra = config.model_extra if config else {}
    timeout = extra.get("timeout", 20)

    try:
        client = _get_bigmodel_client("web_fetch", config=config)
        response = client.web_reader.web_reader(
            url=url,
            return_format="markdown",
            timeout_override=timeout,
        )
    except Exception as e:
        return _tool_error("web_fetch", e)

    reader_result = getattr(response, "reader_result", None)
    if reader_result is None:
        return json.dumps({"error": "web_fetch API call failed", "detail": str(response)})
    title = getattr(reader_result, "title", "") or ""
    content = getattr(reader_result, "content", "") or ""
    truncated = len(content) > WEB_FETCH_MAX_CHARS
    body = content[:WEB_FETCH_MAX_CHARS]
    suffix = "\n\n[...content truncated...]" if truncated else ""
    return f"# {title}\n\n{body}{suffix}"


@tool("ocr", parse_docstring=True)
def ocr_tool(file_path: str) -> str:
    """Extract text from an image file using OCR.

    Args:
        file_path: Path to the image file (PNG, JPG, JPEG, BMP).
    """
    config = get_app_config().get_tool_config("ocr")
    extra = config.model_extra if config else {}
    language_type = extra.get("language_type", "CHN_ENG")

    try:
        client = _get_bigmodel_client("ocr", config=config)
        with _open_validated(file_path) as f:
            response = client.ocr.handwriting_ocr(
                file=f,
                tool_type="hand_write",
                language_type=language_type,
                probability=False,
            )
    except PathAccessError:
        raise
    except Exception as e:
        return _tool_error("ocr", e)

    if getattr(response, "status", "") != "succeeded":
        return json.dumps({"error": "OCR failed", "detail": getattr(response, "message", "unknown error")})

    words_result = getattr(response, "words_result", None) or []
    lines = [getattr(r, "words", "") for r in words_result]
    return "\n".join(lines)


@tool("file_parser", parse_docstring=True)
def file_parser_tool(file_path: str) -> str:
    """Parse a document file and extract its text content.

    Supports PDF, DOCX, XLSX, PPTX, CSV, TXT, MD, PNG, JPG, and more.

    Args:
        file_path: Path to the file to parse.
    """
    config = get_app_config().get_tool_config("file_parser")
    extra = config.model_extra if config else {}
    tool_type = extra.get("tool_type", "lite")
    max_wait = extra.get("max_wait", 120)

    ext = file_path.rsplit(".", 1)[-1].upper() if "." in file_path else ""
    file_type = ext if ext in SUPPORTED_FILE_TYPES else ""

    try:
        client = _get_bigmodel_client("file_parser", config=config)
        with _open_validated(file_path) as f:
            create_resp = client.file_parser.create(
                file=f,
                file_type=file_type,
                tool_type=tool_type,
            )
    except PathAccessError:
        raise
    except Exception as e:
        return _tool_error("file_parser", e)

    task_id = getattr(create_resp, "task_id", None)
    if not task_id:
        return json.dumps({"error": "File parser error", "detail": getattr(create_resp, "message", "unknown error")})

    delay = 3
    deadline = time.time() + max_wait
    try:
        while time.time() < deadline:
            http_resp = client.file_parser.content(
                task_id=task_id,
                format_type="text",
            )
            result = http_resp.json()
            status = result.get("status", "")
            if status == "succeeded":
                content = result.get("content", "")
                truncated = len(content) > FILE_PARSER_MAX_CHARS
                body = content[:FILE_PARSER_MAX_CHARS]
                suffix = "\n\n[...content truncated...]" if truncated else ""
                return f"{body}{suffix}"
            if status not in ("processing",):
                return json.dumps({"error": "File parser failed", "detail": result.get("message", status)})
            time.sleep(delay)
            delay = min(delay * 2, 30)
    except Exception as e:
        return _tool_error("file_parser", e)

    return json.dumps({"error": "File parser timed out", "detail": "Document may be too large or complex"})

"""Unit tests for the BigModel community tools."""

import json
from unittest.mock import MagicMock, mock_open, patch

import pytest


class TestOpenValidated:
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_path_under_user_data_root(self, _mock_file, mock_realpath):
        mock_realpath.return_value = "/mnt/user-data/workspace/file.pdf"

        from deerflow.community.bigmodel.tools import _open_validated

        f = _open_validated("/mnt/user-data/workspace/file.pdf")
        assert f is not None

    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_path_outside_user_data_raises(self, _mock_file, mock_realpath):
        mock_realpath.return_value = "/etc/passwd"

        from deerflow.community.bigmodel.tools import _open_validated

        with pytest.raises(ValueError, match="Access denied"):
            _open_validated("../../../etc/passwd")

    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_path_exactly_user_data_root(self, _mock_file, mock_realpath):
        mock_realpath.return_value = "/mnt/user-data"

        from deerflow.community.bigmodel.tools import _open_validated

        f = _open_validated("/mnt/user-data")
        assert f is not None

    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_substring_match_not_fooled(self, _mock_file, mock_realpath):
        mock_realpath.return_value = "/mnt/user-data-evil/workspace/file.pdf"

        from deerflow.community.bigmodel.tools import _open_validated

        with pytest.raises(ValueError, match="Access denied"):
            _open_validated("/mnt/user-data-evil/workspace/file.pdf")


class TestGetBigmodelClient:
    @patch("deerflow.community.bigmodel.tools.ZhipuAiClient")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_api_key_from_named_tool(self, mock_get_app_config, mock_client_cls):
        config = MagicMock()
        config.model_extra = {"api_key": "named-tool-key"}
        mock_get_app_config.return_value.get_tool_config.return_value = config

        from deerflow.community.bigmodel.tools import _get_bigmodel_client

        _get_bigmodel_client("ocr")
        mock_client_cls.assert_called_once_with(api_key="named-tool-key")

    @patch("deerflow.community.bigmodel.tools.ZhipuAiClient")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_falls_back_to_web_search_config(self, mock_get_app_config, mock_client_cls):
        named_config = MagicMock()
        named_config.model_extra = {}
        fallback_config = MagicMock()
        fallback_config.model_extra = {"api_key": "fallback-key"}

        def get_tool_config(name):
            if name == "web_search":
                return fallback_config
            return named_config

        mock_get_app_config.return_value.get_tool_config.side_effect = get_tool_config

        from deerflow.community.bigmodel.tools import _get_bigmodel_client

        _get_bigmodel_client("ocr")
        mock_client_cls.assert_called_once_with(api_key="fallback-key")

    @patch("deerflow.community.bigmodel.tools.ZhipuAiClient")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_web_search_does_not_fallback_to_itself(self, mock_get_app_config, mock_client_cls):
        search_config = MagicMock()
        search_config.model_extra = {}

        def get_tool_config(name):
            return search_config

        mock_get_app_config.return_value.get_tool_config.side_effect = get_tool_config

        from deerflow.community.bigmodel.tools import _get_bigmodel_client

        with pytest.raises(ValueError, match="No api_key configured"):
            _get_bigmodel_client("web_search")

    @patch("deerflow.community.bigmodel.tools.ZhipuAiClient")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_raises_when_no_key_anywhere(self, mock_get_app_config, mock_client_cls):
        empty = MagicMock()
        empty.model_extra = {}
        mock_get_app_config.return_value.get_tool_config.return_value = empty

        from deerflow.community.bigmodel.tools import _get_bigmodel_client

        with pytest.raises(ValueError, match="No api_key configured"):
            _get_bigmodel_client("file_parser")

    @patch("deerflow.community.bigmodel.tools.ZhipuAiClient")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_uses_passed_config_without_refetching(self, mock_get_app_config, mock_client_cls):
        config = MagicMock()
        config.model_extra = {"api_key": "pre-fetched-key"}

        from deerflow.community.bigmodel.tools import _get_bigmodel_client

        _get_bigmodel_client("ocr", config=config)
        mock_client_cls.assert_called_once_with(api_key="pre-fetched-key")
        mock_get_app_config.assert_not_called()


class TestWebSearchTool:
    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_returns_normalized_results(self, mock_get_app_config, mock_get_client):
        search_config = MagicMock()
        search_config.model_extra = {"max_results": 3, "search_engine": "search_pro"}
        mock_get_app_config.return_value.get_tool_config.return_value = search_config

        r1 = MagicMock()
        r1.title, r1.link, r1.content = "T1", "https://a.com", "S1"
        r2 = MagicMock()
        r2.title, r2.link, r2.content = "T2", "https://b.com", "S2"
        mock_resp = MagicMock()
        mock_resp.search_result = [r1, r2]

        mock_client = MagicMock()
        mock_client.web_search.web_search.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_search_tool

        result = web_search_tool.invoke({"query": "test query"})
        parsed = json.loads(result)

        assert len(parsed) == 2
        assert parsed[0] == {"title": "T1", "url": "https://a.com", "snippet": "S1"}

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_uses_defaults_when_config_missing(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_resp = MagicMock()
        mock_resp.search_result = []

        mock_client = MagicMock()
        mock_client.web_search.web_search.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_search_tool

        web_search_tool.invoke({"query": "test query"})

        call_kwargs = mock_client.web_search.web_search.call_args.kwargs
        assert call_kwargs["count"] == 5
        assert call_kwargs["search_engine"] == "search_pro"

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_api_error_returns_json_error(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None
        mock_resp = MagicMock()
        mock_resp.search_result = None
        mock_client = MagicMock()
        mock_client.web_search.web_search.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_search_tool

        result = web_search_tool.invoke({"query": "test"})
        parsed = json.loads(result)

        assert "error" in parsed
        assert "web_search API call failed" in parsed["error"]

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_sdk_exception_returns_json_error(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None
        mock_get_client.side_effect = ConnectionError("network unreachable")

        from deerflow.community.bigmodel.tools import web_search_tool

        result = web_search_tool.invoke({"query": "test"})
        parsed = json.loads(result)

        assert parsed["error"] == "web_search failed"
        assert "network unreachable" in parsed["detail"]


class TestWebFetchTool:
    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_fetches_and_formats_markdown(self, mock_get_app_config, mock_get_client):
        fetch_config = MagicMock()
        fetch_config.model_extra = {"timeout": 30}
        mock_get_app_config.return_value.get_tool_config.return_value = fetch_config

        reader_data = MagicMock()
        reader_data.title, reader_data.content = "Page Title", "Page content here"
        mock_resp = MagicMock()
        mock_resp.reader_result = reader_data

        mock_client = MagicMock()
        mock_client.web_reader.web_reader.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_fetch_tool

        result = web_fetch_tool.invoke({"url": "https://example.com"})

        assert result == "# Page Title\n\nPage content here"
        mock_client.web_reader.web_reader.assert_called_once()
        call_kwargs = mock_client.web_reader.web_reader.call_args.kwargs
        assert call_kwargs["timeout_override"] == 30

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_default_timeout_when_config_missing(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None

        reader_data = MagicMock()
        reader_data.title, reader_data.content = "T", "C"
        mock_resp = MagicMock()
        mock_resp.reader_result = reader_data

        mock_client = MagicMock()
        mock_client.web_reader.web_reader.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_fetch_tool

        web_fetch_tool.invoke({"url": "https://example.com"})
        assert mock_client.web_reader.web_reader.call_args.kwargs["timeout_override"] == 20

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_truncation_adds_suffix(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None

        reader_data = MagicMock()
        reader_data.title, reader_data.content = "Long", "A" * 5000
        mock_resp = MagicMock()
        mock_resp.reader_result = reader_data

        mock_client = MagicMock()
        mock_client.web_reader.web_reader.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_fetch_tool

        result = web_fetch_tool.invoke({"url": "https://example.com"})

        assert "[...content truncated...]" in result
        assert len(result) < 5000

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_api_error_returns_json_error(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None
        mock_resp = MagicMock()
        mock_resp.reader_result = None
        mock_client = MagicMock()
        mock_client.web_reader.web_reader.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import web_fetch_tool

        result = web_fetch_tool.invoke({"url": "https://example.com"})
        parsed = json.loads(result)

        assert "error" in parsed
        assert "web_fetch API call failed" in parsed["error"]

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    def test_sdk_exception_returns_json_error(self, mock_get_app_config, mock_get_client):
        mock_get_app_config.return_value.get_tool_config.return_value = None
        mock_get_client.side_effect = TimeoutError("request timed out")

        from deerflow.community.bigmodel.tools import web_fetch_tool

        result = web_fetch_tool.invoke({"url": "https://example.com"})
        parsed = json.loads(result)

        assert parsed["error"] == "web_fetch failed"
        assert "request timed out" in parsed["detail"]


class TestOcrTool:
    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-image-data")
    def test_ocr_success(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/scan.png"
        ocr_config = MagicMock()
        ocr_config.model_extra = {"language_type": "ENG"}
        mock_get_app_config.return_value.get_tool_config.return_value = ocr_config

        w1 = MagicMock()
        w1.words = "Hello"
        w2 = MagicMock()
        w2.words = "World"
        mock_resp = MagicMock()
        mock_resp.status = "succeeded"
        mock_resp.words_result = [w1, w2]

        mock_client = MagicMock()
        mock_client.ocr.handwriting_ocr.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import ocr_tool

        result = ocr_tool.invoke({"file_path": "/mnt/user-data/uploads/scan.png"})

        assert result == "Hello\nWorld"
        _, call_kwargs = mock_client.ocr.handwriting_ocr.call_args
        assert call_kwargs["language_type"] == "ENG"

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-image-data")
    def test_ocr_failure_returns_json_error(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/bad.png"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_resp = MagicMock()
        mock_resp.status = "failed"
        mock_resp.message = "unsupported format"

        mock_client = MagicMock()
        mock_client.ocr.handwriting_ocr.return_value = mock_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import ocr_tool

        result = ocr_tool.invoke({"file_path": "/mnt/user-data/uploads/bad.png"})
        parsed = json.loads(result)

        assert parsed["error"] == "OCR failed"
        assert "unsupported format" in parsed["detail"]

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_path_outside_user_data_raises(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/etc/passwd"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        from deerflow.community.bigmodel.tools import ocr_tool

        with pytest.raises(ValueError, match="Access denied"):
            ocr_tool.invoke({"file_path": "../../../etc/passwd"})

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-image-data")
    def test_sdk_exception_returns_json_error(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/scan.png"
        mock_get_app_config.return_value.get_tool_config.return_value = None
        mock_get_client.side_effect = RuntimeError("OCR service unavailable")

        from deerflow.community.bigmodel.tools import ocr_tool

        result = ocr_tool.invoke({"file_path": "/mnt/user-data/uploads/scan.png"})
        parsed = json.loads(result)

        assert parsed["error"] == "ocr failed"
        assert "OCR service unavailable" in parsed["detail"]


class TestFileParserTool:
    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_parser_success(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/doc.pdf"
        parser_config = MagicMock()
        parser_config.model_extra = {"tool_type": "pro", "max_wait": 60}
        mock_get_app_config.return_value.get_tool_config.return_value = parser_config

        mock_create = MagicMock()
        mock_create.task_id = "task-123"

        http_resp = MagicMock()
        http_resp.json.return_value = {"status": "succeeded", "content": "Parsed content"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.return_value = http_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/doc.pdf"})

        assert result == "Parsed content"
        create_kwargs = mock_client.file_parser.create.call_args.kwargs
        assert create_kwargs["file_type"] == "PDF"
        assert create_kwargs["tool_type"] == "pro"

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_parser_defaults_when_config_missing(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/doc.pdf"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-456"

        http_resp = MagicMock()
        http_resp.json.return_value = {"status": "succeeded", "content": "Done"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.return_value = http_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/doc.pdf"})

        create_kwargs = mock_client.file_parser.create.call_args.kwargs
        assert create_kwargs["tool_type"] == "lite"

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_create_error_returns_json_error(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/bad.pdf"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = None
        mock_create.message = "invalid file format"

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/bad.pdf"})
        parsed = json.loads(result)

        assert parsed["error"] == "File parser error"
        assert "invalid file format" in parsed["detail"]

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_parser_polling_retries_then_succeeds(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/doc.pdf"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-poll"

        http1 = MagicMock()
        http1.json.return_value = {"status": "processing"}
        http2 = MagicMock()
        http2.json.return_value = {"status": "processing"}
        http3 = MagicMock()
        http3.json.return_value = {"status": "succeeded", "content": "Final result"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.side_effect = [http1, http2, http3]
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/doc.pdf"})

        assert result == "Final result"
        assert mock_client.file_parser.content.call_count == 3

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_parser_failed_status_returns_json_error(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/doc.pdf"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-fail"

        http_resp = MagicMock()
        http_resp.json.return_value = {"status": "failed", "message": "document corrupted"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.return_value = http_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/doc.pdf"})
        parsed = json.loads(result)

        assert parsed["error"] == "File parser failed"
        assert "document corrupted" in parsed["detail"]

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    @patch("time.sleep")
    @patch("time.time")
    def test_parser_timeout_returns_json_error(self, mock_time, _mock_sleep, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/huge.pdf"

        times = [0.0]
        current = 0.0
        delays = [3, 6, 12, 24, 48, 96]
        for d in delays:
            current += d
            times.append(current)

        mock_time.side_effect = times
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-huge"

        http_resp = MagicMock()
        http_resp.json.return_value = {"status": "processing"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.return_value = http_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/huge.pdf"})
        parsed = json.loads(result)

        assert parsed["error"] == "File parser timed out"

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open)
    def test_path_outside_user_data_raises(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/root/secret.txt"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        from deerflow.community.bigmodel.tools import file_parser_tool

        with pytest.raises(ValueError, match="Access denied"):
            file_parser_tool.invoke({"file_path": "/root/secret.txt"})

    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake-file-data")
    def test_polling_exception_returns_json_error(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/doc.pdf"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-crash"

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.side_effect = ConnectionError("poll failed")
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        result = file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/doc.pdf"})
        parsed = json.loads(result)

        assert parsed["error"] == "file_parser failed"
        assert "poll failed" in parsed["detail"]


class TestFileParserFileTypeMapping:
    @patch("deerflow.community.bigmodel.tools._get_bigmodel_client")
    @patch("deerflow.community.bigmodel.tools.get_app_config")
    @patch("os.path.realpath")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake")
    def test_unknown_extension_passes_empty_string(self, _mock_file, mock_realpath, mock_get_app_config, mock_get_client):
        mock_realpath.return_value = "/mnt/user-data/uploads/unknown.xyz"
        mock_get_app_config.return_value.get_tool_config.return_value = None

        mock_create = MagicMock()
        mock_create.task_id = "task-ext"

        http_resp = MagicMock()
        http_resp.json.return_value = {"status": "succeeded", "content": "done"}

        mock_client = MagicMock()
        mock_client.file_parser.create.return_value = mock_create
        mock_client.file_parser.content.return_value = http_resp
        mock_get_client.return_value = mock_client

        from deerflow.community.bigmodel.tools import file_parser_tool

        file_parser_tool.invoke({"file_path": "/mnt/user-data/uploads/unknown.xyz"})

        assert mock_client.file_parser.create.call_args.kwargs["file_type"] == ""

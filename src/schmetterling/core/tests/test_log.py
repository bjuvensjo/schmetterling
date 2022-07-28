from logging import FileHandler, Formatter, StreamHandler
from unittest.mock import MagicMock, call, patch

from schmetterling.core.log import create_console_handler
from schmetterling.core.log import create_file_handler
from schmetterling.core.log import create_formatter
from schmetterling.core.log import get_handlers
from schmetterling.core.log import log_config
from schmetterling.core.log import log_params_return


@patch("schmetterling.core.log.getLogger", autospec=True)
def test_log_params_return(mock_getLogger):
    mock_log = MagicMock(autospec=True)
    mock_getLogger.return_value = mock_log
    assert 1 == log_params_return()(lambda x: x)(1)
    assert [call("schmetterling.core.tests.test_log")] == mock_getLogger.mock_calls
    assert [
        call.info(
            "%s: %s %s\n=> %s",
            "<lambda>",
            (1,),
            {},
            1,
        )
    ] == mock_log.mock_calls


def test_create_console_handler():
    assert isinstance(
        create_console_handler(create_formatter()),
        StreamHandler,
    )


def test_create_file_handler():
    with patch("schmetterling.core.log.FileHandler", autospec=True):
        assert isinstance(
            create_file_handler(
                "log_dir",
                "log_file",
                create_formatter(),
            ),
            FileHandler,
        )


def test_create_formatter():
    assert isinstance(
        create_formatter(),
        Formatter,
    )


def test_get_handlers():
    with patch("schmetterling.core.log.FileHandler", autospec=True):
        with patch("schmetterling.core.log.StreamHandler", autospec=True):
            handlers = get_handlers(".", "log_file")
            assert 2 == len(handlers)
            assert all(
                [
                    isinstance(handlers["console_handler"], StreamHandler),
                    isinstance(handlers["file_handler"], FileHandler),
                ]
            )


@patch(
    "schmetterling.core.log.get_handlers",
    autospec=True,
    return_value={
        "console_handler": "handler1",
        "file_handler": "handler2",
    },
)
@patch("schmetterling.core.log.getLogger", autospec=True)
@patch("schmetterling.core.log.makedirs", autospec=True)
def test_log_config(mock_makedirs, mock_getLogger, mock_get_handlers):
    mock_log = MagicMock(autospec=True)
    mock_getLogger.return_value = mock_log
    assert log_config(
        "root",
        "name",
        "INFO",
    )
    assert [
        call.setLevel(20),
        call.debug(
            "%s: %s %s\n=> %s",
            "log_config",
            ("root", "name", "INFO"),
            {},
            {"console_handler": "handler1", "file_handler": "handler2"},
        ),
    ] == mock_log.mock_calls
    assert [call("root", exist_ok=True)] == mock_makedirs.mock_calls
    assert [call(), call("schmetterling.core.log")] == mock_getLogger.mock_calls
    assert call("root", "name") == mock_get_handlers.mock_calls[0]
    assert ["handler1", "handler2"] == mock_log.handlers

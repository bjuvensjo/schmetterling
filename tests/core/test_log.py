from logging import FileHandler, Formatter, StreamHandler
from unittest.mock import MagicMock, call, patch

from schmetterling.core.log import (
    create_console_handler,
    create_file_handler,
    create_formatter,
    get_handlers,
    log_config,
    log_params_return,
)


@patch("schmetterling.core.log.getLogger", autospec=True)
def test_log_params_return(mock_getLogger):
    mock_log = MagicMock(autospec=True)
    mock_getLogger.return_value = mock_log
    assert log_params_return()(lambda x: x)(1) == 1
    assert mock_getLogger.mock_calls == [call("tests.core.test_log")]
    assert mock_log.mock_calls == [
        call.info(
            "%s: %s %s\n=> %s",
            "<lambda>",
            (1,),
            {},
            1,
        )
    ]


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
            assert len(handlers) == 2
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
    assert mock_log.mock_calls == [
        call.setLevel(20),
        call.debug(
            "%s: %s %s\n=> %s",
            "log_config",
            ("root", "name", "INFO"),
            {},
            {"console_handler": "handler1", "file_handler": "handler2"},
        ),
    ]
    assert mock_makedirs.mock_calls == [call("root", exist_ok=True)]
    assert mock_getLogger.mock_calls == [call(), call("schmetterling.core.log")]
    assert mock_get_handlers.mock_calls[0] == call("root", "name")
    assert mock_log.handlers == ["handler1", "handler2"]

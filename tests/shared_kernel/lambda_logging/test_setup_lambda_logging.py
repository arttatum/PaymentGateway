import os
import uuid

from shared_kernel.lambda_logging.set_up_logger import (
    add_context,
    configure_context_logger,
    get_logger,
)


def test_get_logger_returns_working_logger(caplog):
    logger = get_logger()
    logger.info("The logger works!")
    assert "The logger works" in caplog.text


def test_configure_lambda_logger_adds_context_to_log_records(caplog):
    some_uuid = str(uuid.uuid4())
    configure_context_logger(new_attribute=some_uuid)
    logger = get_logger()
    logger.info("This record has an extra attribute")
    logger.info("So does this one!")

    for log in caplog.records:
        assert some_uuid in log.new_attribute


def test_add_context_adds_new_attribute_to_log_records(caplog):
    some_uuid = str(uuid.uuid4())
    logger = get_logger()
    logger.info("This record has no extra attributes")
    assert some_uuid not in caplog.text

    add_context(logger, "added_attribute", some_uuid)
    logger.info("This one does!")

    last_log_record = caplog.records[-1]

    assert some_uuid in last_log_record.added_attribute


def test_log_level_is_set_by_environment_variable(capsys):
    os.environ["LOG_LEVEL"] = "ERROR"
    configure_context_logger()
    logger = get_logger()
    logger.info("This record will not be sent to a file descriptor")
    logger.error("This will, awesome!")

    logs = capsys.readouterr().err
    assert "This record will not be sent to a file descriptor" not in logs
    assert "This will, awesome!" in logs


def test_invalid_log_level_defaults_to_INFO(capsys):
    os.environ["LOG_LEVEL"] = "HELLO_WORLD"
    configure_context_logger()
    logger = get_logger()
    logger.info("This record will be sent to a file descriptor")
    logger.debug("This won't be in there, awesome!")

    logs = capsys.readouterr().err
    assert "This record will be sent to a file descriptor" in logs
    assert "This won't be in there, awesome!" not in logs

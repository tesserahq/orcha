from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import run_nats_worker


@pytest.mark.asyncio
async def test_disabled_worker_does_not_log_nats_credentials(monkeypatch):
    settings = SimpleNamespace(
        nats_url="nats://linden_app:secret-password@nats1:4222",
        nats_enabled=False,
        nats_subjects="com.>",
        nats_queue="orcha_worker_all",
    )
    test_logger = Mock()
    monkeypatch.setattr(run_nats_worker, "get_settings", lambda: settings)
    monkeypatch.setattr(run_nats_worker, "logger", test_logger)

    with pytest.raises(SystemExit):
        await run_nats_worker._run_async()

    logged_messages = " ".join(
        str(call.args[0])
        for method in (test_logger.info, test_logger.error)
        for call in method.call_args_list
    )
    assert settings.nats_url not in logged_messages
    assert "secret-password" not in logged_messages
    assert "NATS connection endpoint configured" in logged_messages

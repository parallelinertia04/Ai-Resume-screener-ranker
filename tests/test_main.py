import sys

import main


def test_main_starts_server_on_requested_port(monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["main.py", "--serve", "--port", "9000"])
    monkeypatch.setattr("uvicorn.run", lambda *args, **kwargs: calls.append((args, kwargs)))

    main.main()

    assert calls == [
        (("src.app:app",), {"host": "127.0.0.1", "port": 9000})
    ]


def test_main_uses_default_server_port(monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["main.py", "--serve"])
    monkeypatch.setattr("uvicorn.run", lambda *args, **kwargs: calls.append(kwargs))

    main.main()

    assert calls == [{"host": "127.0.0.1", "port": 8000}]

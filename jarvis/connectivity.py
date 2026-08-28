import socket


def is_online(timeout: float = 1.0) -> bool:
    """Fast connectivity check — one short TCP attempt to a reliable public resolver."""
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=timeout):
            return True
    except OSError:
        return False

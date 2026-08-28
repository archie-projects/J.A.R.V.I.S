import socket


def is_online(timeout: float = 2.0) -> bool:
    """Fast connectivity check — one short TCP handshake on port 443 (HTTPS), since
    that's what actually matters (Groq's API is HTTPS) and it's far less likely to
    be blocked by a router/firewall than raw DNS on port 53."""
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=timeout):
            return True
    except OSError:
        return False

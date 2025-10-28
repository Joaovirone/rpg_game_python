from __future__ import annotations


class Logger:
    """
    Placeholder de logger.
    Mantém a interface para futura troca por logging real.
    """

    def info(self, msg: str) -> None:
        print(f"[LOG] {msg}")

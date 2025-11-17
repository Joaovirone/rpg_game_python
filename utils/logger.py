from __future__ import annotations
import datetime


class Logger:

    def __init__(self):
        self.niveis = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3
        }
        self.nivel_atual = "INFO"
    
    def _formatar_log(self, nivel: str, msg: str) -> str:
        """Formata a mensagem de log de forma consistente."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {nivel}: {msg}"
    
    def _deve_logar(self, nivel: str) -> bool:
        """Verifica se o nível deve ser logado baseado na configuração atual."""
        return self.niveis[nivel] >= self.niveis[self.nivel_atual]
    
    def debug(self, msg: str) -> None:
        if self._deve_logar("DEBUG"):
            print(self._formatar_log("DEBUG", msg))
    
    def info(self, msg: str) -> None:
        if self._deve_logar("INFO"):
            print(self._formatar_log("INFO", msg))
    
    def warning(self, msg: str) -> None:
        if self._deve_logar("WARNING"):
            print(self._formatar_log("WARNING", msg))
    
    def error(self, msg: str) -> None:
        if self._deve_logar("ERROR"):
            print(self._formatar_log("ERROR", msg))
    
    def set_level(self, nivel: str) -> None:
        """Define o nível mínimo de logging."""
        if nivel in self.niveis:
            self.nivel_atual = nivel

logger = Logger()
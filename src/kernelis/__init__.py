"""Kernelis — Agente de Sistemas, Infraestrutura, Ferramentas e Execução Técnica."""

__version__ = "0.1.0"

from kernelis.config import KernelisConfig
from kernelis.core.agent import KernelisAgent

__all__ = ["KernelisAgent", "KernelisConfig", "__version__"]

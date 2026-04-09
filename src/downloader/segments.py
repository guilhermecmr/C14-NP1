from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import threading
import time

# Tamanho de cada bloco lido do socket
HTTP_CHUNK = 512 * 1024

# Limitador de banda global simples (token bucket)
class BandwidthLimiter:
    def __init__(self, bps: Optional[int]):
        self.bps = bps  # None = sem limite
        self._lock = threading.Lock()
        self._tokens = 0.0
        self._capacity = float(bps or 0)
        self._last = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last
        self._last = now
        if self.bps and self.bps > 0:
            self._tokens = min(self._capacity, self._tokens + self.bps * elapsed)
        else:
            self._tokens = float("inf")

    def acquire(self, nbytes: int):
        if self.bps is None or self.bps <= 0:
            return
        with self._lock:
            while True:
                self._refill()
                if self._tokens >= nbytes:
                    self._tokens -= nbytes
                    return
                falta = max(0.0, nbytes - self._tokens)
                time.sleep(min(0.25, falta / self.bps if self.bps > 0 else 0.01))

# Representa um segmento de download
@dataclass
class DownloadSegment:
    index: int # Índice do segmento
    start_byte: int # Byte inicial do segmento
    end_byte: int # Byte final do segmento
    expected_size: int # Tamanho esperado do segmento
    temp_path: str # Caminho temporário do segmento
    downloaded_bytes: int = 0 # Bytes baixados até agora
    start_ts: Optional[float] = None # Timestamp de início do download
    end_ts: Optional[float] = None # Timestamp de término do download
    error_msg: Optional[str] = None # Mensagem de erro, se houver

    @property
    def succeeded(self) -> bool: # Indica se o segmento foi baixado com sucesso
        return self.error_msg is None and self.downloaded_bytes == self.expected_size

    @property
    def duration(self) -> Optional[float]: # Duração do download
        if self.start_ts is None or self.end_ts is None:
            return None
        return max(0.0, self.end_ts - self.start_ts)

    @property
    def avg_bps(self) -> Optional[float]: # Taxa média de download em bytes por segundo
        if not self.duration:
            return None
        return self.downloaded_bytes / self.duration

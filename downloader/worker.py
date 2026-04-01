from __future__ import annotations
import time
import queue
import threading
from typing import Optional
import requests
from .segments import DownloadSegment, HTTP_CHUNK, BandwidthLimiter

# Função para baixar um segmento de arquivo
def download_segment_worker(
    url: str,
    segment: DownloadSegment,
    cancel_event: threading.Event,
    gui_queue: queue.Queue,
    session: requests.Session,
    timeout: int = 30,
    limiter: Optional['BandwidthLimiter'] = None,
) -> None:
    headers = {"Range": f"bytes={segment.start_byte}-{segment.end_byte}"} # Cabeçalho para requisição de intervalo
    segment.start_ts = time.monotonic()
    try:
        with session.get(url, headers=headers, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()
            with open(segment.temp_path, "wb") as fp:
                for data in resp.iter_content(chunk_size=HTTP_CHUNK):
                    if cancel_event.is_set():
                        raise RuntimeError("Operação cancelada pelo usuário")
                    if not data:
                        continue
                    if limiter:
                        limiter.acquire(len(data)) # Controla a largura de banda
                    fp.write(data)
                    segment.downloaded_bytes += len(data)
                    gui_queue.put(("progress", segment.index, segment.downloaded_bytes))
        segment.end_ts = time.monotonic()
    except Exception as exc:
        segment.end_ts = time.monotonic()
        segment.error_msg = str(exc)
        gui_queue.put(("error", segment.index, segment.error_msg))

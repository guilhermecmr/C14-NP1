from __future__ import annotations
import os
import time
import threading
from typing import List, Optional
import requests

from .segments import DownloadSegment, HTTP_CHUNK, BandwidthLimiter
from .net import fetch_head_info
from .io_utils import (
    get_downloads_dir,
    split_in_segments,
    assemble_output_file,
    write_csv_log,
)

from .worker import download_segment_worker

# Função principal para executar o trabalho de download
def run_download_job(
    url: str,
    requested_threads: int,
    out_path: str,
    delete_parts: bool,
    log_format: str,
    gui_queue,
    cancel_event: threading.Event,
    rate_bps: Optional[int] = None,
) -> None:
    session = requests.Session()
    limiter = BandwidthLimiter(rate_bps)
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    except Exception:
        pass
    session.headers.update({"User-Agent": "PyThreadDownloader/1.0"})

    try:
        gui_queue.put(("status", "Coletando informações do servidor (HEAD)...")) 
        total_size, supports_range = fetch_head_info(url, session)
        effective_threads = max(1, min(5, requested_threads))
        if not supports_range or total_size is None:
            effective_threads = 1
        gui_queue.put(("meta", total_size, effective_threads))
        if effective_threads == 1:
            reason = []
            if not supports_range: 
                reason.append("servidor não suporta HTTP Range")
            if total_size is None:
                reason.append("tamanho do arquivo desconhecido")
            if reason:
                gui_queue.put(("status", "Modo 1 thread porque: " + ", ".join(reason)))

        requested_name = (os.path.basename(out_path) if out_path else os.path.basename(requests.utils.urlparse(url).path)) or "download.bin"

        downloads_dir = get_downloads_dir()
        file_stem, _ = os.path.splitext(requested_name)
        download_dir = os.path.join(downloads_dir, file_stem or "download")
        log_dir  = os.path.join(download_dir, "log")
        temp_dir = os.path.join(download_dir, "temp")
        os.makedirs(log_dir,  exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        base_name = requested_name
        out_path  = os.path.join(download_dir, base_name)

        if total_size is not None:
            segments = split_in_segments(total_size, effective_threads, base_name)
            for seg in segments:
                seg.temp_path = os.path.join(temp_dir, f"part{seg.index}")
        else:
            segments = [DownloadSegment(0, 0, 0, 0, os.path.join(temp_dir, "part0"))]

        for seg in segments:
            gui_queue.put(("init_part", seg.index, seg.expected_size))

        threads: List[threading.Thread] = []
        gui_queue.put(("status", f"Iniciando {len(segments)} thread(s) de download..."))

        if len(segments) == 1 and total_size is None:
            seg = segments[0]
            seg.start_ts = time.monotonic()
            try:
                with session.get(url, stream=True, timeout=30) as resp:
                    resp.raise_for_status()
                    with open(seg.temp_path, "wb") as fp:
                        for data in resp.iter_content(chunk_size=HTTP_CHUNK):
                            if limiter:
                                limiter.acquire(len(data))
                            if cancel_event.is_set():
                                raise RuntimeError("Operação cancelada pelo usuário")
                            if not data:
                                continue
                            fp.write(data)
                            seg.downloaded_bytes += len(data)
                            gui_queue.put(("progress", seg.index, seg.downloaded_bytes))
                seg.end_ts = time.monotonic()
            except Exception as exc:
                seg.end_ts = time.monotonic()
                seg.error_msg = str(exc)
                gui_queue.put(("error", seg.index, seg.error_msg))
        else:
            for seg in segments:
                t = threading.Thread(
                    target=download_segment_worker,
                    args=(url, seg, cancel_event, gui_queue, session),
                    kwargs={"timeout": 30, "limiter": limiter},
                    daemon=True,
                )
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

        overall_success = all(seg.succeeded for seg in segments)
        if not overall_success:
            failed = [f"part{seg.index}:{seg.error_msg}" for seg in segments if not seg.succeeded]
            gui_queue.put(("status", "Falha em partes: " + ", ".join(failed)))

        log_path: Optional[str] = None
        if overall_success:
            gui_queue.put(("status", "Montando arquivo final..."))
            assemble_output_file(out_path, segments)
            gui_queue.put(("status", f"Arquivo salvo em: {out_path}"))

        try:
            log_path = os.path.join(log_dir, "log.csv")
            starts = [s.start_ts for s in segments if s.start_ts is not None]
            ends = [s.end_ts for s in segments if s.end_ts is not None]
            total_time_s = (max(ends) - min(starts)) if starts and ends else 0.0
            write_csv_log(log_path, url, segments, total_size, effective_threads, total_time_s)
            gui_queue.put(("status", f"Log salvo em: {log_path}"))
        except Exception as exc:
            gui_queue.put(("status", f"Falha ao escrever log: {exc}"))

        if overall_success and delete_parts:
            for seg in segments:
                try:
                    os.remove(seg.temp_path)
                except OSError:
                    pass
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass

        gui_queue.put(("done", overall_success, out_path, log_path))

    except Exception as exc:
        gui_queue.put(("status", f"Erro não tratado: {exc}"))
        gui_queue.put(("done", False, out_path, None))

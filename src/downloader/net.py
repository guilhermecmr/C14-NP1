from __future__ import annotations
from typing import Optional, Tuple
import requests

# Obtém informações do cabeçalho do arquivo
def fetch_head_info(url: str, session: requests.Session, timeout: int = 15) -> Tuple[Optional[int], bool]:
    total: Optional[int] = None
    supports = False
    try: # Tenta obter informações via HEAD
        r = session.head(url, allow_redirects=True, timeout=timeout)
        if r.status_code < 400: 
            if r.headers.get("Content-Length", "").isdigit():
                total = int(r.headers["Content-Length"]) # Tamanho total do arquivo
            supports = "bytes" in r.headers.get("Accept-Ranges", "").lower()
    except Exception:
        pass
    if (total is None or not supports):
        try: # Tenta obter informações via GET
            headers = {"Range": "bytes=0-0"}
            r = session.get(url, headers=headers, stream=True, timeout=timeout)
            if r.status_code == 206:
                supports = True
                cr = r.headers.get("Content-Range", "") # Intervalo de conteúdo
                if "/" in cr:
                    total = int(cr.split("/")[-1])
        except Exception:
            pass
    return total, supports

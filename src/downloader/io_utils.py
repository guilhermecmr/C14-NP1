from __future__ import annotations
import os
from typing import Optional, List
from .segments import DownloadSegment

# Obtém o diretório de downloads do usuário
def get_downloads_dir() -> str:
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    os.makedirs(downloads, exist_ok=True)
    return downloads

# Formata um número de bytes em uma string legível
def format_bytes(num: Optional[int]) -> str:
    if num is None:
        return "?"
    n = float(num)
    if n < 1024:
        return f"{int(n)} B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        n /= 1024.0
        if n < 1024:
            return f"{n:.2f} {unit}"
    return f"{n:.2f} PiB"

# Converte "500KiB/s", "2MiB/s", "150000" (bytes/s) em inteiro de bytes/s; vazio = sem limite
def parse_rate_to_bps(text: str) -> Optional[int]:
    if not text:
        return None
    s = text.strip().lower().replace(" ", "")
    for suf in ("/s", "ps"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    mult = 1
    for suf, m in (("kib", 1024), ("kb", 1024), ("k", 1024),
                   ("mib", 1024*1024), ("mb", 1024*1024), ("m", 1024*1024),
                   ("gib", 1024**3), ("gb", 1024**3), ("g", 1024**3)):
        if s.endswith(suf):
            s = s[: -len(suf)]
            mult = m
            break
    try:
        return max(1, int(float(s) * mult))
    except ValueError:
        return None

# Divide o download em segmentos
def split_in_segments(total_bytes: int, n: int, basename: str) -> List[DownloadSegment]:
    n = max(1, n) # Garante que haja pelo menos um segmento
    base = total_bytes // n # Tamanho base de cada segmento
    rem = total_bytes % n # Resto a ser distribuído
    segments: List[DownloadSegment] = []
    offset = 0 # Offset atual (posição inicial do próximo segmento)
    for i in range(n):
        size = base + (1 if i < rem else 0)
        start = offset
        end = offset + size - 1
        temp_path = f"{basename}.part{i}"
        segments.append(DownloadSegment(i, start, end, size, temp_path))
        offset += size
    return segments

# Monta o arquivo de saída a partir dos segmentos baixados
def assemble_output_file(out_path: str, segments: List[DownloadSegment]) -> None:
    with open(out_path, "wb") as out:
        for seg in sorted(segments, key=lambda s: s.index): # Ordena os segmentos pela ordem de índice
            with open(seg.temp_path, "rb") as part:
                while True:
                    chunk = part.read(1024 * 1024) # Lê 1 MiB de cada vez
                    if not chunk:
                        break 
                    out.write(chunk)

# Escreve um log em formato CSV
def write_csv_log(
    path: str, # Caminho do arquivo CSV
    url: str, # URL do arquivo
    segments: List[DownloadSegment], # Segmentos baixados
    total_bytes: Optional[int], # Tamanho total do arquivo
    threads_used: int, # Número de threads utilizadas
    total_time_s: float, # Tempo total (segundos)
) -> None:
    base = os.path.basename(path)
    arquivo_nome = base[:-4] if base.lower().endswith(".csv") else os.path.splitext(base)[0]

    headers = [ # Cabeçalhos do CSV
        "Arquivo",
        "URL",
        "Threads Utilizadas",
        "Tamanho Total (bytes)",
        "Tempo Total (segundos)",
    ]
    values = [ # Valores do CSV
        arquivo_nome,
        url,
        str(threads_used),
        str(total_bytes) if total_bytes is not None else "?",
        f"{total_time_s:.3f}",
    ]

    for idx, s in enumerate(sorted(segments, key=lambda x: x.index), start=1): # Itera sobre os segmentos
        dur = s.duration or 0.0
        avg_mib_s = (s.avg_bps or 0.0) / (1024 * 1024)
        headers += [
            f"Bytes Baixados (Thread {idx})",
            f"Velocidade Média (Thread {idx}, MiB/s)",
            f"Tamanho da Parte (Thread {idx}, bytes)",
            f"Tempo (Thread {idx}, seg)",
        ]
        values += [
            str(s.downloaded_bytes),
            f"{avg_mib_s:.3f}",
            str(s.expected_size),
            f"{dur:.3f}",
        ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(";".join(headers) + "\n")
        f.write(";".join(values) + "\n")

from downloader.io_utils import format_bytes, parse_rate_to_bps, split_in_segments, assemble_output_file, write_csv_log
from downloader.segments import DownloadSegment

##########################
# Testes de fluxo normal #
##########################

# Teste para verificar a formatação de bytes em KiB
def test_format_bytes():
    assert format_bytes(2048) == "2.00 KiB"

# Teste para verificar a conversão da taxa de transferência
def test_parse_rate(): 
    assert parse_rate_to_bps("1MiB/s") == 1024 * 1024

# Teste para verificar a divisão de um arquivo em segmentos iguais
def test_split_segments(): # 
    segments = split_in_segments(100, 2, "file")

    assert len(segments) == 2
    assert segments[0].expected_size == 50
    assert segments[1].expected_size == 50

# Teste para verificar a montagem de um arquivo a partir de segmentos
def test_assemble_file(tmp_path): 
    pt1 = tmp_path/"p1"
    pt2 = tmp_path/"p2"
    output = tmp_path/"output"

    pt1.write_text("parte1")
    pt2.write_text("parte2")

    seg1 = DownloadSegment(0, 0, 0, 6, str(pt1))
    seg2 = DownloadSegment(1, 0, 0, 6, str(pt2))

    assemble_output_file(str(output), [seg1, seg2])

    assert output.read_text() == "parte1parte2"

# Teste para verificar a formatação de bytes abaixo de 1 KiB
def test_format_bytes_bytes():
    assert format_bytes(512) == "512 B"

# Teste para verificar a conversão da taxa de transferência em KiB/s
def test_parse_rate_kib():
    assert parse_rate_to_bps("2KiB/s") == 2 * 1024

# Teste para verificar a divisão de um arquivo em segmentos desiguais
def test_split_segments_uneven():
    segments = split_in_segments(10, 3, "file")

    assert len(segments) == 3
    assert segments[0].expected_size == 4
    assert segments[1].expected_size == 3
    assert segments[2].expected_size == 3

# Teste para verificar a montagem de um arquivo a partir de segmentos fora de ordem
def test_assemble_file_out_of_order(tmp_path):
    pt1 = tmp_path/"p1"
    pt2 = tmp_path/"p2"
    output = tmp_path/"output"

    pt1.write_text("parte1")
    pt2.write_text("parte2")

    seg1 = DownloadSegment(0, 0, 0, 6, str(pt1))
    seg2 = DownloadSegment(1, 0, 0, 6, str(pt2))

    assemble_output_file(str(output), [seg2, seg1])

    assert output.read_text() == "parte1parte2"

# Teste para verificar a escrita de um log CSV
def test_write_csv_log(tmp_path):
    output = tmp_path/"log.csv"
    seg = DownloadSegment(0, 0, 9, 10, "tmp", downloaded_bytes=10, start_ts=0.0, end_ts=2.0)

    write_csv_log(str(output), "http://teste", [seg], 10, 1, 2.0)

    assert "Arquivo;URL;Threads Utilizadas" in output.read_text()

###############################
# Testes de fluxo de extensão #
###############################

# Teste para verificar a formatação de bytes quando o valor é None
def test_format_bytes_none():
    assert format_bytes(None) == "?"

# Teste para verificar a conversão da taxa de transferência com formato inválido
def test_parse_rate_invalid():
    assert parse_rate_to_bps("invalid") is None

# Teste para verificar a divisão de um arquivo em segmentos com número de threads igual a zero
def test_split_segments_zero_threads():
    segments = split_in_segments(100, 0, "file")

    assert len(segments) == 1

# Teste para verificar a conversão da taxa de transferência quando o valor é vazio
def test_parse_rate_empty():
    assert parse_rate_to_bps("") is None

# Teste para verificar a divisão de um arquivo vazio em segmentos
def test_split_segments_zero_bytes():
    segments = split_in_segments(0, 2, "file")

    assert len(segments) == 2
    assert segments[0].expected_size == 0
    assert segments[1].expected_size == 0

# Teste para verificar a montagem de um arquivo sem segmentos
def test_assemble_file_empty(tmp_path):
    output = tmp_path/"output"

    assemble_output_file(str(output), [])

    assert output.read_text() == ""

# Teste para verificar a escrita de um log CSV sem tamanho total conhecido
def test_write_csv_log_none_total(tmp_path):
    output = tmp_path/"log.csv"
    seg = DownloadSegment(0, 0, 9, 10, "tmp")

    write_csv_log(str(output), "http://teste", [seg], None, 1, 0.0)

    assert "?" in output.read_text()

# Teste falho 
def test_format_bytes():
    assert format_bytes(1000) == "2.00 KiB"
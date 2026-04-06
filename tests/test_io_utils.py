from downloader.io_utils import format_bytes, parse_rate_to_bps, split_in_segments, assemble_output_file
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
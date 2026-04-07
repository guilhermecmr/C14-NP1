from downloader.segments import DownloadSegment

##########################
# Testes de fluxo normal #
##########################

# Teste para verificar o sucesso do download de um segmento
def test_segment_success():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 10

    assert seg.succeeded is True

# Teste para verificar a duração de um segmento com tempo de início e fim válidos
def test_segment_duration():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.start_ts = 1.0
    seg.end_ts = 3.0

    assert seg.duration == 2.0

# Teste para verificar a taxa média de download de um segmento
def test_segment_avg_bps():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 10
    seg.start_ts = 0.0
    seg.end_ts = 2.0

    assert seg.avg_bps == 5.0

###############################
# Testes de fluxo de extensão #
###############################

# Teste para verificar a montagem de um arquivo a partir de segmentos quando um segmento falhou
def test_segment_failure():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 5

    assert seg.succeeded is False

# Teste para verificar a duração de um segmento sem tempo de início ou fim
def test_segment_duration_none():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")

    assert seg.duration is None

# Teste para verificar a falha do download de um segmento quando há mensagem de erro
def test_segment_failure_with_error():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 10
    seg.error_msg = "erro"

    assert seg.succeeded is False

# Teste para verificar a taxa média de download de um segmento sem duração válida
def test_segment_avg_bps_none():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 10

    assert seg.avg_bps is None

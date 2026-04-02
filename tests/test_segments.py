from downloader.segments import DownloadSegment

##########################
# Testes de fluxo normal #
##########################

# Teste para verificar o sucesso do download de um segmento
def test_segment_success():
    seg = DownloadSegment(0, 0, 10, 10, "tmp")
    seg.downloaded_bytes = 10

    assert seg.succeeded is True

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
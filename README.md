# Downloader Multithread com GUI

![CI/CD Pipeline](https://github.com/guilhermecmr/C14-NP1/actions/workflows/cicd.yml/badge.svg)

Projeto desenvolvido para a disciplina de Engenharia de Software. A aplicação foi construída em Python com interface em Tkinter e realiza downloads em múltiplas threads, dividindo o arquivo em partes e montando o arquivo final ao término da transferência.

## Integrantes

- Guilherme
- Luan Robert

## Funcionalidades

- Download de arquivos em múltiplas threads
- Interface gráfica com Tkinter
- Montagem automática do arquivo final
- Geração de logs do processo de download
- Pipeline CI/CD com testes, build, cobertura, deploy e notificação

## Estrutura do Projeto

- [`src/app.py`](/home/luan/Documentos/Projetos/C14-NP1/src/app.py): ponto de entrada da aplicação
- [`src/downloader/`](/home/luan/Documentos/Projetos/C14-NP1/src/downloader): lógica principal de download, segmentação, rede e IO
- [`src/gui/`](/home/luan/Documentos/Projetos/C14-NP1/src/gui): interface gráfica
- [`tests/`](/home/luan/Documentos/Projetos/C14-NP1/tests): testes unitários
- [`scripts/send_notification.py`](/home/luan/Documentos/Projetos/C14-NP1/scripts/send_notification.py): script de envio de e-mail ao final do pipeline
- [`.github/workflows/cicd.yml`](/home/luan/Documentos/Projetos/C14-NP1/.github/workflows/cicd.yml): pipeline CI/CD
- [`pyproject.toml`](/home/luan/Documentos/Projetos/C14-NP1/pyproject.toml): configuração do pacote Python

## Requisitos

- Python 3.9 ou superior
- `tkinter` disponível no ambiente para execução da interface
- Dependências listadas em [`requirements.txt`](/home/luan/Documentos/Projetos/C14-NP1/requirements.txt)

Instalação das dependências:

```bash
pip install -r requirements.txt
```

Instalação do projeto em modo local:

```bash
pip install -e .
```

## Como Executar

Depois de instalar o projeto:

```bash
c14-np1
```

Alternativamente, a partir da raiz do projeto:

```bash
PYTHONPATH=src python -m app
```

## Como Rodar os Testes

Execução dos testes unitários:

```bash
python -m pytest
```

Execução com geração de relatório JUnit:

```bash
python -m pytest --junitxml=report.xml
```

## Cobertura de Testes

O projeto utiliza `pytest-cov` para gerar relatório de cobertura em HTML.

```bash
python -m pytest --cov=downloader --cov=gui --cov=app --cov-report=html
```

O relatório gerado fica na pasta `htmlcov/`.

## Pipeline CI/CD

O projeto possui um pipeline configurado no GitHub Actions com as seguintes etapas:

1. `tests`
Executa os testes unitários e salva o relatório `report.xml` como artifact.

2. `build`
Gera a distribuição do pacote Python com `python -m build` e publica o conteúdo de `dist/` como artifact.

3. `coverage`
Executa os testes com cobertura e publica o relatório HTML como artifact.

4. `pypi-publish`
Publica o pacote no PyPI após o sucesso das etapas de build e cobertura.

5. `notification`
Executa um script Python externo para enviar um e-mail com o resumo final do pipeline.

## Paralelismo do Pipeline

Após a etapa `tests`, os jobs `build` e `coverage` podem prosseguir de forma independente. Isso atende ao requisito de possuir jobs em paralelo dentro do pipeline.

## Artifacts Gerados

- `test-report`: relatório dos testes unitários
- `release-dists`: arquivos gerados em `dist/`
- `coverage-report`: relatório HTML de cobertura

## Deploy

O deploy adotado neste projeto é a publicação do pacote Python no PyPI, caracterizando deploy de artefato de build.

Projeto no PyPI:

- `https://pypi.org/project/c14-np1/`

Para a publicação automática funcionar, o repositório precisa estar configurado no PyPI como Trusted Publisher ou usar autenticação por token de API.

## Notificação por E-mail

A etapa de notificação utiliza o script [`send_notification.py`](/home/luan/Documentos/Projetos/C14-NP1/scripts/send_notification.py ) e depende dos seguintes secrets no GitHub Actions:

- `EMAIL_USER`
- `EMAIL_PASS`
- `NOTIFICATION_EMAIL`

Opcionalmente, também podem ser definidos:

- `SMTP_SERVER`
- `SMTP_PORT`

O script envia um resumo com o status de:

- testes
- build
- cobertura
- deploy

## Testes Implementados

O projeto possui mais de 20 cenários de testes unitários cobrindo:

- fluxo principal de segmentação e montagem de arquivos
- formatação e conversão de taxas e tamanhos
- casos de erro e entradas inválidas
- cenários de borda, como valores vazios, zero e ordenação de partes

Arquivos de teste:

- [`tests/test_segments.py`](/home/luan/Documentos/Projetos/C14-NP1/tests/test_segments.py)
- [`tests/test_io_utils.py`](/home/luan/Documentos/Projetos/C14-NP1/tests/test_io_utils.py)

## Links de Teste

Alguns arquivos públicos que podem ser usados para validar a aplicação:

- [100 MB](https://ash-speed.hetzner.com/100MB.bin)
- [1 GB](https://ash-speed.hetzner.com/1GB.bin)
- [10 GB](https://ash-speed.hetzner.com/10GB.bin)

## Uso de IA

Ferramentas de IA foram utilizadas como apoio para:

- revisão da estrutura do workflow CI/CD
- refinamento da documentação
- organização incremental das etapas do pipeline

As sugestões geradas foram revisadas e adaptadas manualmente antes de serem incorporadas ao projeto.

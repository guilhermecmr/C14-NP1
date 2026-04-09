# Downloader Multithread com GUI

Projeto desenvolvido para a disciplina de Engenharia de Software. A aplicação foi construída em Python com interface em Tkinter e realiza downloads em múltiplas threads, dividindo o arquivo em partes para melhorar o desempenho e montar o resultado final ao término da transferência.

## Integrantes

- Guilherme
- Luan Robert

## Funcionalidades

- Download de arquivos em múltiplas threads
- Interface gráfica com Tkinter
- Montagem automática do arquivo final
- Geração de logs auxiliares do processo de download

## Estrutura do Projeto

- [`app.py`](/home/luan/Documentos/Projetos/C14-NP1/app.py): ponto de entrada da aplicação
- [`downloader/`](/home/luan/Documentos/Projetos/C14-NP1/downloader): lógica principal de download, segmentação e IO
- [`gui/`](/home/luan/Documentos/Projetos/C14-NP1/gui): interface gráfica
- [`tests/`](/home/luan/Documentos/Projetos/C14-NP1/tests): testes unitários
- [`.github/workflows/cicd.yml`](/home/luan/Documentos/Projetos/C14-NP1/.github/workflows/cicd.yml): pipeline CI/CD

## Requisitos

- Python 3.9 ou superior
- Dependências listadas em [`requirements.txt`](/home/luan/Documentos/Projetos/C14-NP1/requirements.txt)

Instalação das dependências:

```bash
pip install -r requirements.txt
```

## Como Executar

Para iniciar a aplicação:

```bash
python app.py
```

## Como Rodar os Testes

Execução dos testes unitários:

```bash
pytest
```

Execução com geração de relatório JUnit:

```bash
pytest --junitxml=report.xml
```

## Cobertura de Testes

O projeto utiliza `pytest-cov` para gerar relatório de cobertura em HTML.

```bash
pytest --cov=downloader --cov=gui --cov=app --cov-report=html
```

O relatório gerado fica na pasta `htmlcov/`.

## Pipeline CI/CD

O projeto possui um pipeline configurado no GitHub Actions com as seguintes etapas:

1. `tests`
   Executa os testes unitários e salva o relatório como artifact.
2. `build`
   Gera o pacote distribuível da aplicação.
3. `coverage`
   Executa os testes com cobertura e armazena o relatório HTML como artifact.
4. `pypi-publish`
   Etapa de deploy/publicação do pacote para o PyPI.
5. `notification`
   Executa um script externo para envio de notificação por e-mail ao final do pipeline.

## Artifacts Gerados

- `test-report`: relatório dos testes unitários
- `release-dists`: arquivos gerados em `dist/`
- `coverage-report`: relatório HTML de cobertura

## Deploy

O deploy adotado neste projeto é a publicação do pacote Python no PyPI, caracterizando deploy de artefato de build. Essa etapa ocorre no workflow do GitHub Actions após as validações do pipeline.

## Testes Implementados

O projeto possui mais de 20 cenários de testes unitários cobrindo:

- fluxo principal de segmentação e montagem de arquivos
- formatação e conversão de taxas e tamanhos
- casos de erro e entradas inválidas
- cenários de borda, como valores vazios, zero e ordenação de partes

## Links de Teste

Alguns arquivos públicos que podem ser usados para validar a aplicação:

- [100 MB](https://ash-speed.hetzner.com/100MB.bin)
- [1 GB](https://ash-speed.hetzner.com/1GB.bin)
- [10 GB](https://ash-speed.hetzner.com/10GB.bin)


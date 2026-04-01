# Downloader Multithread com GUI

Um simples gerenciador de downloads multithread escrito em **Python + Tkinter**.  
Ele divide o arquivo em partes, baixa cada parte em threads paralelas e monta o arquivo final.  
Os downloads são salvos automaticamente na pasta **Downloads**, com subpastas `log/` e `temp/`.

---

## 🔗 Links de Teste

Você pode usar estes links de exemplo para testar o funcionamento:

- [100 MB](https://ash-speed.hetzner.com/100MB.bin)  
- [1 GB](https://ash-speed.hetzner.com/1GB.bin)  
- [10 GB](https://ash-speed.hetzner.com/10GB.bin)  

---

## 📦 Requisitos

- Python 3.9 ou superior  
- Dependências listadas em `requirements.txt`  

Instale as dependências com:

```bash
pip install -r requirements.txt
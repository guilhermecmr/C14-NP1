from __future__ import annotations
import os
import queue
import threading
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, messagebox

from downloader.orchestrator import run_download_job
from downloader.io_utils import format_bytes

# Classe para a interface gráfica do downloader
class DownloaderGUI(ttk.Frame):
    def __init__(self, master: tk.Tk): # Inicializa a interface gráfica
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        master.title("Downloader Multithread")
        master.minsize(720, 450)

        self.gui_queue: queue.Queue = queue.Queue() # Fila para comunicação com a interface gráfica
        self.cancel_event = threading.Event() # Evento para cancelar o download
        self.worker_thread: Optional[threading.Thread] = None # Thread de download
        self.part_progressbars: List[ttk.Progressbar] = [] # Barras de progresso por parte
        self.part_labels: List[ttk.Label] = [] # Labels por parte
        self.part_expected_sizes: List[int] = [] # Tamanhos esperados por parte
        self.total_size: Optional[int] = None # Tamanho total do arquivo
        self.effective_threads: int = 1 # Número efetivo de threads

        self._build_widgets()
        self._poll_gui_queue()

    def _build_widgets(self) -> None: # Constrói os widgets da interface gráfica
        pad = {"padx": 8, "pady": 6}
        cfg_box = ttk.LabelFrame(self, text="Configurações")
        cfg_box.pack(fill="x", **pad)

        # URL
        ttk.Label(cfg_box, text="URL:").grid(row=0, column=0, sticky="w")
        self.entry_url = ttk.Entry(cfg_box, width=72)
        self.entry_url.grid(row=0, column=1, columnspan=6, sticky="we", padx=6)
        cfg_box.columnconfigure(6, weight=1)

        # Salvar como
        ttk.Label(cfg_box, text="Salvar como:").grid(row=1, column=0, sticky="w")
        self.entry_out = ttk.Entry(cfg_box, width=40)
        self.entry_out.grid(row=1, column=1, sticky="we", padx=6)

        # Threads
        ttk.Label(cfg_box, text="Threads (1–5):").grid(row=1, column=2, sticky="e", padx=(10, 5))
        self.spin_threads = ttk.Spinbox(cfg_box, from_=1, to=5, width=5)
        self.spin_threads.set("4")
        self.spin_threads.grid(row=1, column=3, sticky="w", padx=(0, 15))

        # Apagar partes ao final
        self.var_delete_parts = tk.BooleanVar(value=True)
        ttk.Checkbutton(cfg_box, text="Apagar partes ao final", variable=self.var_delete_parts).grid(
            row=1, column=4, sticky="w", padx=(15, 0)
        )

        # Botões
        self.btn_start = ttk.Button(cfg_box, text="Iniciar", command=self._on_start)
        self.btn_start.grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.btn_cancel = ttk.Button(cfg_box, text="Cancelar", command=self._on_cancel, state="disabled")
        self.btn_cancel.grid(row=3, column=1, sticky="w", pady=(8, 0))

        # Progresso total
        total_box = ttk.LabelFrame(self, text="Progresso Total")
        total_box.pack(fill="x", **pad)
        self.lbl_total = ttk.Label(total_box, text="Aguardando...")
        self.lbl_total.pack(anchor="w", padx=8, pady=4)
        self.pb_total = ttk.Progressbar(total_box, mode="determinate")
        self.pb_total.pack(fill="x", padx=8, pady=(0, 8))

        # Partes
        self.parts_box = ttk.LabelFrame(self, text="Partes (por thread)")
        self.parts_box.pack(fill="both", expand=True, **pad)

        # Status
        self.lbl_status = ttk.Label(self, text="Pronto.")
        self.lbl_status.pack(fill="x", padx=8, pady=6)

    # Reseta a interface de partes
    def _reset_parts_ui(self, count: int) -> None:
        for w in self.part_progressbars + self.part_labels:
            w.destroy()
        self.part_progressbars.clear()
        self.part_labels.clear()
        self.part_expected_sizes = [0] * count
        for i in range(count):
            lbl = ttk.Label(self.parts_box, text=f"Parte {i}: 0 / ?")
            lbl.grid(row=i, column=0, sticky="w", padx=8, pady=2)
            pb = ttk.Progressbar(self.parts_box, mode="determinate")
            pb.grid(row=i, column=1, sticky="we", padx=8, pady=2)
            self.parts_box.columnconfigure(1, weight=1)
            self.part_labels.append(lbl)
            self.part_progressbars.append(pb)

    # Inicia o download
    def _on_start(self) -> None:
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Entrada inválida", "Informe uma URL.")
            return
        try:
            n_threads = int(self.spin_threads.get())
        except ValueError:
            n_threads = 4
        n_threads = max(1, min(5, n_threads))

        out_path = self.entry_out.get().strip() # Caminho de saída
        log_format = "csv" # Formato de log

        # Desabilita os widgets durante o download
        for w in (self.btn_start, self.entry_url, self.entry_out, self.spin_threads):
            w.configure(state="disabled")
        self.btn_cancel.configure(state="normal")

        # Atualiza o status e o progresso
        self.lbl_total.config(text="Preparando...")
        self.pb_total.configure(mode="determinate", maximum=100, value=0)
        self._reset_parts_ui(1)

        # Limpa o evento de cancelamento
        self.cancel_event.clear()
        self.worker_thread = threading.Thread(
            target=run_download_job,
            args=(
                url,
                n_threads,
                out_path,
                self.var_delete_parts.get(),
                log_format,
                self.gui_queue,
                self.cancel_event,
            ),
            daemon=True,
        )
        self.worker_thread.start()

    def _on_cancel(self) -> None: # Cancela o download
        if self.worker_thread and self.worker_thread.is_alive():
            self.cancel_event.set()
            self.lbl_status.config(text="Cancelando...")
            self.btn_cancel.configure(state="disabled")

    def _poll_gui_queue(self) -> None: # Verifica a fila de eventos da GUI
        try:
            while True:
                event = self.gui_queue.get_nowait()
                self._handle_worker_event(event)
        except queue.Empty:
            pass
        self.after(100, self._poll_gui_queue)

    def _handle_worker_event(self, event) -> None: # Trata os eventos do trabalhador
        kind = event[0]
        if kind == "status": # Atualiza o status
            _, text = event
            self.lbl_status.config(text=text)
        elif kind == "meta": # Atualiza os metadados
            _, total_bytes, eff_threads = event
            self.total_size = total_bytes
            self.effective_threads = eff_threads
            self._reset_parts_ui(eff_threads)
            if total_bytes is None:
                self.pb_total.configure(mode="indeterminate")
                self.pb_total.start(80)
                self.lbl_total.config(text="Baixando (tamanho desconhecido)...")
            else:
                self.pb_total.configure(mode="determinate", maximum=total_bytes, value=0)
                self.lbl_total.config(text=f"Total: 0 / {format_bytes(total_bytes)}")
        elif kind == "init_part": # Inicializa a parte
            _, index, expected_size = event
            self.part_expected_sizes[index] = expected_size
            bar = self.part_progressbars[index]
            bar.configure(maximum=expected_size, value=0)
            self.part_labels[index].config(text=f"Parte {index}: 0 / {format_bytes(expected_size)}")
        elif kind == "progress": # Atualiza o progresso da parte
            _, index, downloaded = event
            bar = self.part_progressbars[index]
            bar.configure(value=downloaded)
            label_text = f"Parte {index}: {format_bytes(downloaded)}"
            if self.part_expected_sizes[index]: # Se o tamanho esperado da parte for conhecido
                label_text += f" / {format_bytes(self.part_expected_sizes[index])}"
            self.part_labels[index].config(text=label_text)
            if self.total_size is not None: # Se o tamanho total for conhecido
                total_downloaded = sum(pb["value"] for pb in self.part_progressbars)
                self.pb_total.configure(value=total_downloaded)
                self.lbl_total.config(
                    text=f"Total: {format_bytes(int(total_downloaded))} / {format_bytes(self.total_size)}"
                )
        elif kind == "error": # Atualiza a parte com erro
            _, index, message = event
            self.part_labels[index].config(text=f"Parte {index}: ERRO — {message}")
        elif kind == "done": # Finaliza o download
            _, success, out_path, log_path = event
            self.btn_start.configure(state="normal")
            self.btn_cancel.configure(state="disabled")
            for w in (self.entry_url, self.entry_out, self.spin_threads):
                w.configure(state="normal")
            if str(self.pb_total.cget("mode")) == "indeterminate": # Se o modo da barra de progresso for indeterminado
                self.pb_total.stop()
            if success: # Se o download foi bem-sucedido
                self.lbl_status.config(text="Concluído com sucesso.")
                self.lbl_total.config(text=f"Concluído: {out_path}")
                msg = "Download concluído.\n\n"
                msg += f"Arquivo:\n{os.path.abspath(out_path)}\n"
                messagebox.showinfo("Sucesso", msg)
            else: # Se o download falhou
                self.lbl_status.config(text="Falha no download.")
                messagebox.showerror("Erro", "Falha no download. Verifique o status e tente novamente.")

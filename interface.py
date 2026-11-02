import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import os
import sys
import math

# Garante que o Python encontre o job_hunter.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from job_hunter import executar_agente

# Configurações de aparência do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class AgenteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuração da Janela em Tela Cheia ---
        self.title("Agente de Vagas - Leandro")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False)) 

        # =========================================================
        # AQUI ENTRA A IMAGEM DE FUNDO (A Dica de Ouro)
        # =========================================================
        try:
            # Tenta carregar a imagem bg.png da mesma pasta
            img_pil = Image.open("bg.png")
            # Redimensiona para o tamanho exato da tela do monitor
            img_pil = img_pil.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(img_pil)

            # Cria um Canvas que ocupa a tela inteira para ser o fundo
            self.bg_canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), highlightthickness=0)
            self.bg_canvas.pack(fill="both", expand=True)
            # Coloca a imagem no Canvas
            self.bg_canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except FileNotFoundError:
            # Se não achar o bg.png, apenas ignora e deixa o fundo escuro padrão
            self.bg_canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), highlightthickness=0, bg="#1E1E1E")
            self.bg_canvas.pack(fill="both", expand=True)

        # =========================================================
        # FRAME CENTRAL (Fica por cima da imagem)
        # =========================================================
        # Cria o frame, mas ainda não posiciona ele na tela
        self.frame_central = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=20, bg_color="transparent")
        
        # Coloca o frame no centro da tela, DENTRO do Canvas de fundo
        self.bg_canvas.create_window(
            self.winfo_screenwidth() // 2,  # Metade da largura da tela (X)
            self.winfo_screenheight() // 2, # Metade da altura da tela (Y)
            window=self.frame_central,
            anchor="center"
        )

        # --- Animação do Ícone (Círculo Pulsante) ---
        # O Canvas da animação tem que ter a mesma cor do frame (#1E1E1E)
        self.canvas = tk.Canvas(self.frame_central, width=150, height=150, 
                                bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(pady=(30, 20), padx=50)
        
        self.pulso = self.canvas.create_oval(25, 25, 125, 125, fill="#2FA572", outline="")
        self.animar_pulso()

        # --- Títulos ---
        self.titulo = ctk.CTkLabel(
            self.frame_central, 
            text="AGENTE DE BUSCA", 
            font=("Segoe UI", 32, "bold"),
            text_color="#FFFFFF"
        )
        self.titulo.pack(pady=(10, 5))

        self.subtitulo = ctk.CTkLabel(
            self.frame_central, 
            text="Vagas Júnior / Estágio / Trainee • São Paulo ou Remoto", 
            font=("Segoe UI", 16),
            text_color="#A0A0A0"
        )
        self.subtitulo.pack(pady=(0, 40))

        # --- Botão de Busca ---
        self.botao = ctk.CTkButton(
            self.frame_central,
            text="🔍 Iniciar Busca",
            font=("Segoe UI", 18, "bold"),
            height=50,
            width=250,
            corner_radius=25,
            fg_color="#2FA572",
            hover_color="#238A5D",
            command=self.iniciar_busca
        )
        self.botao.pack(pady=20)

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(
            self.frame_central, 
            text="Sistema pronto.", 
            font=("Segoe UI", 14),
            text_color="#A0A0A0"
        )
        self.status_label.pack(pady=(0, 30))

    def animar_pulso(self):
        """Cria o efeito de pulsar no ícone central."""
        self.angulo = getattr(self, 'angulo', 0) + 0.1
        raio = 50 + (math.sin(self.angulo) * 5)
        
        x0 = 75 - raio
        y0 = 75 - raio
        x1 = 75 + raio
        y1 = 75 + raio
        self.canvas.coords(self.pulso, x0, y0, x1, y1)
        
        self.after(50, self.animar_pulso)

    def iniciar_busca(self):
        self.botao.configure(state="disabled", text="Buscando...")
        self.status_label.configure(text="⏳ Executando agente... Isso pode levar alguns minutos.", text_color="#F1C40F")

        def tarefa():
            try:
                executar_agente()
                self.status_label.configure(text="✅ Busca concluída com sucesso!", text_color="#2FA572")
                messagebox.showinfo("Sucesso", "Busca concluída!\nVerifique a pasta output.")
            except Exception as e:
                self.status_label.configure(text=f"❌ Erro: {e}", text_color="#E74C3C")
                messagebox.showerror("Erro", f"Ocorreu um erro:\n\n{e}")
            finally:
                self.botao.configure(state="normal", text="🔍 Iniciar Busca")

        threading.Thread(target=tarefa, daemon=True).start()

if __name__ == "__main__":
    app = AgenteApp()
    app.mainloop()
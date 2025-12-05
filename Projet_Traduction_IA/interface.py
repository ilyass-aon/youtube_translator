import customtkinter as ctk
import threading
from core.downloader import AudioDownloader
from core.transcriber import AudioTranscriber
from core.translator import UniversalTranslator
from core.summarizer import TextSummarizer # <--- Nouvel import

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Video Studio (Traduction & Résumé)")
        self.geometry("900x700")

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # La zone des onglets prend tout l'espace

        # ================= HEADER (Commun) =================
        self.frame_header = ctk.CTkFrame(self)
        self.frame_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.label_title = ctk.CTkLabel(self.frame_header, text="📺 AI Video Studio", font=("Roboto Medium", 20))
        self.label_title.pack(side="left", padx=20, pady=10)

        self.entry_url = ctk.CTkEntry(self.frame_header, placeholder_text="Collez le lien YouTube ici...", width=400)
        self.entry_url.pack(side="left", padx=10, expand=True, fill="x")

        # ================= STATUS BAR =================
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.label_status = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.label_status.grid(row=3, column=0, pady=(0, 10))

        # ================= ONGLETS (Tabview) =================
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # --- Création des onglets ---
        self.tab_trad = self.tabview.add("Traduction")
        self.tab_sum = self.tabview.add("Résumé")

        #setup des onglets
        self.setup_tab_traduction()
        self.setup_tab_resume()

    def setup_tab_traduction(self):
        """Contenu de l'onglet Traduction"""
        t = self.tab_trad
        t.grid_columnconfigure(0, weight=1)
        t.grid_rowconfigure(1, weight=1)

        # Contrôles
        self.frame_controls_trad = ctk.CTkFrame(t, fg_color="transparent")
        self.frame_controls_trad.grid(row=0, column=0, sticky="ew", pady=10)

        self.option_lang = ctk.CTkOptionMenu(self.frame_controls_trad, values=["fr", "ar", "en", "es", "de"])
        self.option_lang.pack(side="left", padx=5)
        self.option_lang.set("fr")

        self.btn_trad = ctk.CTkButton(self.frame_controls_trad, text="Lancer Traduction", command=self.start_translation_thread)
        self.btn_trad.pack(side="right", padx=5)

        # Resultat
        self.textbox_trad = ctk.CTkTextbox(t, font=("Arial", 12))
        self.textbox_trad.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.textbox_trad.insert("0.0", "La traduction apparaîtra ici...")

    def setup_tab_resume(self):
        """Contenu de l'onglet Résumé"""
        t = self.tab_sum
        t.grid_columnconfigure(0, weight=1)
        t.grid_rowconfigure(1, weight=1)

        # Contrôles
        self.frame_controls_sum = ctk.CTkFrame(t, fg_color="transparent")
        self.frame_controls_sum.grid(row=0, column=0, sticky="ew", pady=10)

        self.lbl_info = ctk.CTkLabel(self.frame_controls_sum, text="Génère un résumé court du contenu vidéo.")
        self.lbl_info.pack(side="left", padx=5)

        self.btn_sum = ctk.CTkButton(self.frame_controls_sum, text="Générer Résumé", fg_color="#E07A5F", hover_color="#D16045", command=self.start_summary_thread)
        self.btn_sum.pack(side="right", padx=5)

        # Resultat
        self.textbox_sum = ctk.CTkTextbox(t, font=("Arial", 12))
        self.textbox_sum.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.textbox_sum.insert("0.0", "Le résumé apparaîtra ici...")

    # ================= LOGIQUE (Threads) =================

    def update_status(self, progress, text):
        self.progress_bar.set(progress)
        self.label_status.configure(text=text)
        self.update_idletasks()

    def start_translation_thread(self):
        url = self.entry_url.get()
        if not url: return
        self.btn_trad.configure(state="disabled")
        threading.Thread(target=self.run_translation, args=(url,)).start()

    def start_summary_thread(self):
        url = self.entry_url.get()
        if not url: return
        self.btn_sum.configure(state="disabled")
        threading.Thread(target=self.run_summary, args=(url,)).start()

    def get_audio_and_transcribe(self, url):
        """Fonction utilitaire partagée : DL + Transcribe"""
        # 1. DL
        self.update_status(0.1, "Téléchargement...")
        downloader = AudioDownloader()
        path = downloader.download(url)
        if not path: raise Exception("Erreur DL")

        # 2. Transcribe
        self.update_status(0.3, "Transcription (Whisper)...")
        transcriber = AudioTranscriber()
        res = transcriber.transcribe(path)
        return res

    def run_translation(self, url):
        try:
            res = self.get_audio_and_transcribe(url)
            if not res: return
            
            self.update_status(0.5, "Traduction (NLLB)...")
            translator = UniversalTranslator()
            
            # Callback pour la barre
            def progress_cb(p): self.progress_bar.set(0.5 + (p*0.5))

            final = translator.translate(res["text"], res["language"], self.option_lang.get(), progress_callback=progress_cb)
            
            self.textbox_trad.delete("0.0", "end")
            self.textbox_trad.insert("0.0", final)
            self.update_status(1.0, "Traduction terminée !")

        except Exception as e:
            self.update_status(0, f"Erreur: {e}")
        finally:
            self.btn_trad.configure(state="normal")

    def run_summary(self, url):
        try:
            res = self.get_audio_and_transcribe(url)
            if not res: return

            self.update_status(0.6, "Génération du résumé (BART)...")
            summarizer = TextSummarizer()
            
            # Note: On résume le texte original transcrit
            summary = summarizer.summarize(res["text"])
            
            self.textbox_sum.delete("0.0", "end")
            self.textbox_sum.insert("0.0", summary)
            self.update_status(1.0, "Résumé terminé !")

        except Exception as e:
            self.update_status(0, f"Erreur: {e}")
        finally:
            self.btn_sum.configure(state="normal")

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
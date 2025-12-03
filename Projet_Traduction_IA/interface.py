import customtkinter as ctk
import threading
from core.downloader import AudioDownloader
from core.transcriber import AudioTranscriber
from core.translator import UniversalTranslator

# Configuration visuelle
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Video Translator Pro")
        self.geometry("800x600")

        # Grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # La zone de résultat s'étire

        # 1. Titre
        self.label_title = ctk.CTkLabel(self, text="Traducteur Vidéo Universel", font=("Roboto Medium", 22))
        self.label_title.grid(row=0, column=0, pady=(20, 10))

        # 2. Zone URL
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.entry_url = ctk.CTkEntry(self.frame_input, placeholder_text="Collez le lien YouTube ici...", height=40)
        self.entry_url.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        # 3. Zone Contrôles (Langue + Bouton)
        self.frame_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controls.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.lbl_lang = ctk.CTkLabel(self.frame_controls, text="Langue de sortie :")
        self.lbl_lang.pack(side="left", padx=5)

        self.option_lang = ctk.CTkOptionMenu(self.frame_controls, values=["fr", "ar", "en", "es", "de", "it"])
        self.option_lang.pack(side="left", padx=5)
        self.option_lang.set("fr")

        self.btn_start = ctk.CTkButton(self.frame_controls, text="TRADUIRE", command=self.start_thread, height=40, font=("Roboto", 14, "bold"))
        self.btn_start.pack(side="right", padx=10)

        # 4. Barre de progression & Statut
        self.label_status = ctk.CTkLabel(self, text="En attente...", text_color="gray")
        self.label_status.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.progress_bar.set(0) # 0%

        # 5. Zone de Résultat (Grande zone de texte)
        self.textbox_result = ctk.CTkTextbox(self, font=("Arial", 14), wrap="word")
        self.textbox_result.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        self.textbox_result.insert("0.0", "Le résultat de la traduction s'affichera ici.")
        self.textbox_result.configure(state="disabled") # Lecture seule au début

    def update_ui_status(self, progress, message):
        """Met à jour la barre et le texte de statut"""
        self.progress_bar.set(progress)
        self.label_status.configure(text=message)
        self.update_idletasks() # Force la mise à jour visuelle

    def start_thread(self):
        url = self.entry_url.get()
        if not url: return
        
        self.btn_start.configure(state="disabled")
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.configure(state="disabled")
        
        threading.Thread(target=self.run_pipeline, args=(url, self.option_lang.get())).start()

    def run_pipeline(self, url, target_lang):
        try:
            # ETAPE 1 : Téléchargement (0% -> 20%)
            self.update_ui_status(0.1, " Téléchargement de l'audio...")
            downloader = AudioDownloader()
            audio_path = downloader.download(url)
            
            if not audio_path: raise Exception("Échec téléchargement")

            # ETAPE 2 : Transcription (20% -> 50%)
            self.update_ui_status(0.3, "Transcription IA et détection langue...")
            transcriber = AudioTranscriber()
            res = transcriber.transcribe(audio_path)
            
            if not res: raise Exception("Échec transcription")
            
            source_text = res["text"]
            detected_lang = res["language"]
            self.update_ui_status(0.5, f"Langue détectée : {detected_lang}. Traduction en cours...")

            # ETAPE 3 : Traduction (50% -> 100%)
            translator = UniversalTranslator()
            
            # Fonction interne pour mettre à jour la barre PENDANT la traduction
            def progress_handler(percent_done):
                # On map 0-100% de traduction sur la plage 0.5-1.0 de la barre globale
                global_progress = 0.5 + (percent_done * 0.5)
                # On utilise after() pour mettre à jour l'UI depuis le thread secondaire
                self.after(0, lambda: self.progress_bar.set(global_progress))

            final_text = translator.translate(
                source_text, 
                detected_lang, 
                target_lang, 
                progress_callback=progress_handler
            )

            # Affichage final
            self.update_ui_status(1.0, " Terminé !")
            self.show_result_in_box(final_text)

        except Exception as e:
            self.update_ui_status(0, " Erreur")
            self.show_result_in_box(f"Une erreur est survenue : {str(e)}")
        
        finally:
            self.btn_start.configure(state="normal")

    def show_result_in_box(self, text):
        """Affiche le texte final dans la boite"""
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", text)
        self.textbox_result.configure(state="disabled") # Rendre non-éditable

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
import yt_dlp
import os
from config import OUTPUT_DIR

class AudioDownloader:
    def __init__(self, output_dir=OUTPUT_DIR):
        self.output_dir = output_dir

    def download(self, url):
        """
        Télécharge l'audio depuis une URL YouTube.
        Retourne : Le chemin absolu du fichier mp3 ou None si erreur.
        """
        print(f"[Downloader] Démarrage du téléchargement : {url}")
        
        # Nom temporaire pour le fichier
        filename = "temp_audio"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, f'{filename}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Reconstruction du chemin final (yt-dlp ajoute l'extension automatiquement)
            final_path = os.path.join(self.output_dir, f"{filename}.mp3")
            
            if os.path.exists(final_path):
                print(f" [Downloader] Fichier prêt : {final_path}")
                return final_path
            else:
                print(" [Downloader] Erreur : Fichier introuvable après téléchargement.")
                return None

        except Exception as e:
            print(f" [Downloader] Exception critique : {e}")
            return None
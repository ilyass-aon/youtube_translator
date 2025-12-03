import whisper
import os
import torch
from config import MODEL_WHISPER, DEVICE

class AudioTranscriber:
    def __init__(self):
        """
        Initialise le modèle Whisper.
        Le chargement se fait une seule fois à l'instanciation de la classe.
        """
        print(f" [Transcriber] Chargement du modèle Whisper '{MODEL_WHISPER}' sur {DEVICE}...")
        try:
            self.model = whisper.load_model(MODEL_WHISPER, device=DEVICE)
            print(" [Transcriber] Modèle chargé avec succès.")
        except Exception as e:
            print(f" [Transcriber] Erreur critique au chargement du modèle : {e}")
            raise e

    def transcribe(self, audio_path):
        """
        Transcrit un fichier audio et détecte la langue.
        
        Args:
            audio_path (str): Chemin vers le fichier mp3.
            
        Returns:
            dict: {
                "text": str,       # Le texte transcrit
                "language": str,   # Code langue (ex: 'zh', 'en', 'fr')
                "segments": list   # (Optionnel) Détails temporels pour les sous-titres
            }
        """
        if not os.path.exists(audio_path):
            print(f" [Transcriber] Fichier introuvable : {audio_path}")
            return None

        print(f" [Transcriber] Analyse de l'audio en cours...")
        
        try:
            # L'inférence se fait ici.
            # On ne force pas la langue (task="transcribe" par défaut) pour laisser Whisper détecter.
            result = self.model.transcribe(audio_path)
            
            detected_lang = result.get('language', 'unknown')
            text_len = len(result.get('text', ''))
            
            print(f" [Transcriber] Terminé. Langue détectée : [{detected_lang.upper()}]. Taille texte : {text_len} chars.")
            
            return {
                "text": result["text"],
                "language": detected_lang,
                # On garde les segments si plus tard on veut faire des sous-titres (.srt)
                "segments": result["segments"] 
            }

        except Exception as e:
            print(f" [Transcriber] Erreur lors de la transcription : {e}")
            return None
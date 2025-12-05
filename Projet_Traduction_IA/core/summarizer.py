from transformers import pipeline
import torch
from config import DEVICE

class TextSummarizer:
    def __init__(self):
        # Modèle optimisé pour le résumé (Rapide et léger)
        # Note: Fonctionne le mieux sur des textes en Anglais.
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        
        print(f" [Summarizer] Chargement du modèle '{self.model_name}'...")
        try:
            self.summarizer = pipeline(
                "summarization", 
                model=self.model_name, 
                device=0 if DEVICE == "cuda" else -1
            )
        except Exception as e:
            print(f" Erreur chargement Summarizer: {e}")
            self.summarizer = None

    def summarize(self, text, ratio=0.3):
        """
        Args:
            text (str): Le texte à résumer.
            ratio (float): Le pourcentage de la taille originale (0.3 = 30%).
        """
        if not self.summarizer:
            return "Erreur: Modèle non chargé."

        # Sécurité : Les transformers ont une limite de tokens (souvent 1024)
        # Pour ce MVP, on tronque le texte s'il est trop long pour éviter le crash.
        # Une version V2 ferait un découpage par blocs.
        max_input_chars = 4000 
        text_processed = text[:max_input_chars]
        
        input_len = len(text_processed)
        print(f" [Summarizer] Résumé en cours sur {input_len} caractères...")

        try:
            # Calcul dynamique de la longueur cible
            # On veut un résumé entre 50 mots min et (ratio)% du texte max
            word_count = len(text_processed.split())
            max_len = int(word_count * ratio)
            min_len = int(word_count * 0.1)
            
            # Bornes de sécurité pour le modèle
            if max_len > 150: max_len = 150
            if min_len < 30: min_len = 30
            if max_len < min_len: max_len = min_len + 10

            result = self.summarizer(
                text_processed, 
                max_length=max_len, 
                min_length=min_len, 
                do_sample=False
            )
            
            return result[0]['summary_text']
            
        except Exception as e:
            print(f" Erreur résumé : {e}")
            return text 
# pour exec sur console locale 
import os
import time
from core.downloader import AudioDownloader
from core.transcriber import AudioTranscriber
from core.translator import UniversalTranslator
from config import OUTPUT_DIR

def main():
    print("==================================================")
    print("      🎥 TRADUCTEUR VIDÉO UNIVERSEL IA 🤖       ")
    print("==================================================")

    # 1. INPUTS UTILISATEUR
    url = input("\n Entrez l'URL YouTube : ").strip()
    if not url: return

    target_lang = input(" Langue cible (fr, ar, en, es...) : ").strip().lower()
    if not target_lang: target_lang = "fr" # Par défaut

    start_time = time.time()

    # 2. TÉLÉCHARGEMENT
    downloader = AudioDownloader()
    audio_path = downloader.download(url)
    
    if not audio_path:
        print(" Arrêt du programme (Erreur Download).")
        return

    try:
        # 3. TRANSCRIPTION
        transcriber = AudioTranscriber()
        transcription_result = transcriber.transcribe(audio_path)
        
        if not transcription_result:
            print(" Arrêt du programme (Erreur Transcription).")
            return

        source_text = transcription_result["text"]
        detected_lang = transcription_result["language"]

        # Sauvegarde transcription originale
        filename_orig = f"transcription_{detected_lang}.txt"
        path_orig = os.path.join(OUTPUT_DIR, filename_orig)
        with open(path_orig, "w", encoding="utf-8") as f:
            f.write(source_text)
        print(f" Transcription sauvegardée : {filename_orig}")

        # 4. TRADUCTION
        translator = UniversalTranslator()
        final_translation = translator.translate(
            text=source_text,
            source_lang_whisper=detected_lang,
            target_lang_whisper=target_lang
        )

        # Sauvegarde traduction
        filename_trad = f"traduction_{target_lang}.txt"
        path_trad = os.path.join(OUTPUT_DIR, filename_trad)
        with open(path_trad, "w", encoding="utf-8") as f:
            f.write(final_translation)
        
        print("\n" + "="*50)
        print(f"SUCCÈS TOTAL !")
        print(f" Temps total : {round(time.time() - start_time, 2)} secondes")
        print(f" Fichier résultat : {path_trad}")
        print("="*50)

    except Exception as e:
        print(f" Une erreur inattendue est survenue : {e}")
    
    finally:
        # Nettoyage optionnel du fichier audio pour gagner de la place
        # if os.path.exists(audio_path): os.remove(audio_path)
        pass

if __name__ == "__main__":
    main()
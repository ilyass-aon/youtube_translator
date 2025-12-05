# test de telechargement et transcription audio
from core.downloader import AudioDownloader
from core.transcriber import AudioTranscriber

def test_pipeline():
    # 1. Test Download
    downloader = AudioDownloader()
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" 
    path = downloader.download(url)
    
    if path:
        # 2. Test Transcribe
        transcriber = AudioTranscriber()
        result = transcriber.transcribe(path)
        
        if result:
            print("\n--- RÉSULTAT TEST ---")
            print(f"Langue : {result['language']}")
            print(f"Extrait : {result['text'][:100]}...")
        else:
            print("Echec Transcription")
    else:
        print("Echec Download")

if __name__ == "__main__":
    test_pipeline()
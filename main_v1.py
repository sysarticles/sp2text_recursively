import os
import speech_recognition as sr
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# --- AYARLAR .env dosyasından okunur ---
# Lütfen projenizin ana dizininde bir .env dosyası oluşturun ve
# ROOT_FOLDER ile OUTPUT_FOLDER değişkenlerini orada tanımlayın.
ROOT_FOLDER = os.getenv("ROOT_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "Cikti_Dosyalari") # .env'de yoksa varsayılan değer

# Hata günlüğü dosyası, ROOT_FOLDER'ın içine yerleştirilecek.
# ROOT_FOLDER tanımlıysa yol oluşturulur, değilse None olur.
ERROR_LOG_FILE = os.path.join(ROOT_FOLDER, "hatali_dosyalar.txt") if ROOT_FOLDER else None

# --- WHISPER MODELİ AYARI ---
# Kullanılacak Whisper modelini seçin. Seçenekler: "tiny", "base", "small", "medium", "large"
# Öneri: İyi bir başlangıç için "base" veya "small" modellerini kullanabilirsiniz.
# Daha doğru sonuçlar için "medium" veya "large" kullanabilirsiniz ancak daha yavaş çalışır.
WHISPER_MODEL = "large"


def transcribe_audio(file_path, root_folder):
    """
    Verilen yoldaki bir ses dosyasını OpenAI Whisper kullanarak metne çevirir.
    Hata almamak için önce dosyayı geçici bir WAV dosyasına dönüştürür.
    """
    # --- DOSYA ADI OLUŞTURMA MANTIĞI ---
    try:
        relative_path = os.path.relpath(file_path, root_folder)
        path_without_ext, _ = os.path.splitext(relative_path)
        new_filename_base = path_without_ext.replace(os.sep, '_')
        new_filename_txt = new_filename_base + ".txt"
        output_txt_path = os.path.join(OUTPUT_FOLDER, new_filename_txt)
    except Exception as e:
        print(f"   [HATA] Dosya yolu oluşturulurken hata: {e} - Dosya: {file_path}")
        log_error(f"Dosya yolu hatası: {e} - Dosya: {file_path}")
        return

    # Eğer metin dosyası zaten varsa, bu adımı atla
    if os.path.exists(output_txt_path):
        print(f"-> Zaten mevcut, atlanıyor: {os.path.basename(output_txt_path)}")
        return

    print(f"-> İşleniyor: {os.path.basename(file_path)} (Model: {WHISPER_MODEL})")

    temp_wav_file = None
    try:
        # --- HATA DÜZELTMESİ: pydub ile WAV'a çevirme ---
        # Ses dosyasını formatına bakmaksızın pydub ile yükle
        sound = AudioSegment.from_file(file_path)
        
        # Geçici bir WAV dosyası oluştur
        temp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sound.export(temp_wav_file.name, format="wav")
        # --- Düzeltme sonu ---

        r = sr.Recognizer()
        # Geçici WAV dosyasını kullanarak deşifre et
        with sr.AudioFile(temp_wav_file.name) as source:
            audio_data = r.record(source)
        
        text = r.recognize_whisper(
            audio_data,
            model=WHISPER_MODEL,
            language="turkish"
        )

        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"   [BAŞARILI] -> {os.path.basename(output_txt_path)} oluşturuldu.")

    except Exception as e:
        error_message = f"Beklenmedik bir hata oluştu: {e}: {file_path}"
        print(f"   [HATA] -> {error_message}")
        log_error(error_message)
    finally:
        # Geçici WAV dosyasını her durumda sil
        if temp_wav_file and os.path.exists(temp_wav_file.name):
            try:
                temp_wav_file.close()
                os.unlink(temp_wav_file.name)
            except Exception as e:
                print(f"   [UYARI] Geçici dosya silinemedi: {e}")


def log_error(message):
    """Hata mesajlarını bir dosyaya kaydeder."""
    if not ERROR_LOG_FILE:
        print("Hata: Kök klasör (ROOT_FOLDER) tanımlanmadığı için hata günlüğü yazılamıyor.")
        return
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def main():
    """
    Ana fonksiyon. Belirtilen klasörde gezinir ve ses dosyalarını işler.
    """
    if not ROOT_FOLDER or not os.path.isdir(ROOT_FOLDER):
        print("Hata: Lütfen .env dosyanızda ROOT_FOLDER değişkenini geçerli bir klasör yolu olarak ayarlayın.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        try:
            os.makedirs(OUTPUT_FOLDER)
            print(f"'{OUTPUT_FOLDER}' adında çıktı klasörü oluşturuldu.")
        except Exception as e:
            print(f"Çıktı klasörü oluşturulamadı: {e}")
            return

    print(f"'{ROOT_FOLDER}' klasörü ve alt klasörleri taranıyor...")
    
    for dirpath, _, filenames in os.walk(ROOT_FOLDER):
        for filename in filenames:
            if filename.lower().endswith((".mp3", ".m4a")):
                full_path = os.path.join(dirpath, filename)
                transcribe_audio(full_path, ROOT_FOLDER)
    
    print("\nİşlem tamamlandı.")
    if ERROR_LOG_FILE and os.path.exists(ERROR_LOG_FILE):
        print(f"Bazı dosyalarda hatalar oluştu. Detaylar için '{ERROR_LOG_FILE}' dosyasına bakınız.")

if __name__ == "__main__":
    main()

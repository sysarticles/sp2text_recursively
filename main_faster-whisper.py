import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile
import datetime
import time

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# --- AYARLAR .env dosyasından okunur ---
ROOT_FOLDER = os.getenv("ROOT_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "Cikti_Dosyalari")

# Hata günlüğü dosyası, ROOT_FOLDER'ın içine yerleştirilecek.
ERROR_LOG_FILE = os.path.join(ROOT_FOLDER, "hatali_dosyalar.txt") if ROOT_FOLDER else None

# --- WHISPER MODELİ AYARI ---
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


def log_with_timestamp(message):
    """Mesajların başına zaman damgası ekleyerek konsola yazar."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def transcribe_audio(file_path, root_folder):
    """
    Verilen yoldaki bir ses dosyasını OpenAI Whisper kullanarak metne çevirir.
    İşlem adımlarını ve süresini zaman damgalarıyla günlüğe kaydeder.
    """
    # --- DOSYA ADI OLUŞTURMA MANTIĞI ---
    try:
        relative_path = os.path.relpath(file_path, root_folder)
        path_without_ext, _ = os.path.splitext(relative_path)
        new_filename_base = path_without_ext.replace(os.sep, '_')
        new_filename_txt = new_filename_base + ".txt"
        output_txt_path = os.path.join(OUTPUT_FOLDER, new_filename_txt)
    except Exception as e:
        log_with_timestamp(f"   [HATA] Dosya yolu oluşturulurken hata: {e} - Dosya: {file_path}")
        log_error(f"Dosya yolu hatası: {e} - Dosya: {file_path}")
        return

    # Eğer metin dosyası zaten varsa, bu adımı atla
    if os.path.exists(output_txt_path):
        log_with_timestamp(f"-> Zaten mevcut, atlanıyor: {os.path.basename(output_txt_path)}")
        return

    log_with_timestamp(f"İşlem başlıyor: {os.path.basename(file_path)} (Model: {WHISPER_MODEL})")
    
    start_time = time.time()
    temp_wav_file = None
    try:
        # Adım 1: WAV formatına çevirme
        log_with_timestamp("   -> Adım 1: Ses dosyası WAV formatına çevriliyor...")
        sound = AudioSegment.from_file(file_path)
        temp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sound.export(temp_wav_file.name, format="wav")
        log_with_timestamp("   -> Adım 1: WAV formatına çevirme tamamlandı.")

        # Adım 2: Metne çevirme
        log_with_timestamp("   -> Adım 2: Metne çevirme işlemi (Whisper) başlıyor... (Bu adım uzun sürebilir)")

        # from faster_whisper import WhisperModel

        model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")

        segments, info = model.transcribe(temp_wav_file.name, language="tr")

        text = "".join([segment.text for segment in segments])
        #  print(text)


        log_with_timestamp("   -> Adım 2: Metne çevirme tamamlandı.")

        # Adım 3: Dosyaya yazma
        log_with_timestamp("   -> Adım 3: Metin dosyası diske yazılıyor...")
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        duration = time.time() - start_time
        log_with_timestamp(f"[BAŞARILI] -> {os.path.basename(output_txt_path)} oluşturuldu. Toplam süre: {duration:.2f} saniye.")

    except Exception as e:
        duration = time.time() - start_time
        error_message = f"Beklenmedik bir hata oluştu: {e}: {file_path}. Geçen süre: {duration:.2f} saniye."
        log_with_timestamp(f"   [HATA] -> {error_message}")
        log_error(error_message)
    finally:
        # Geçici WAV dosyasını her durumda sil
        if temp_wav_file and os.path.exists(temp_wav_file.name):
            try:
                temp_wav_file.close()
                os.unlink(temp_wav_file.name)
            except Exception as e:
                log_with_timestamp(f"   [UYARI] Geçici dosya silinemedi: {e}")


def log_error(message):
    """Hata mesajlarını zaman damgasıyla bir dosyaya kaydeder."""
    if not ERROR_LOG_FILE:
        log_with_timestamp("Hata: Kök klasör (ROOT_FOLDER) tanımlanmadığı için hata günlüğü yazılamıyor.")
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    """
    Ana fonksiyon. Belirtilen klasörde gezinir ve ses dosyalarını işler.
    """
    if not ROOT_FOLDER or not os.path.isdir(ROOT_FOLDER):
        log_with_timestamp("Hata: Lütfen .env dosyanızda ROOT_FOLDER değişkenini geçerli bir klasör yolu olarak ayarlayın.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        try:
            os.makedirs(OUTPUT_FOLDER)
            log_with_timestamp(f"'{OUTPUT_FOLDER}' adında çıktı klasörü oluşturuldu.")
        except Exception as e:
            log_with_timestamp(f"Çıktı klasörü oluşturulamadı: {e}")
            return

    log_with_timestamp(f"'{ROOT_FOLDER}' klasörü ve alt klasörleri taranıyor...")
    
    for dirpath, _, filenames in os.walk(ROOT_FOLDER):
        for filename in filenames:
            if filename.lower().endswith((".mp3", ".m4a")):
                full_path = os.path.join(dirpath, filename)
                transcribe_audio(full_path, ROOT_FOLDER)
    
    log_with_timestamp("İşlem tamamlandı.")
    if ERROR_LOG_FILE and os.path.exists(ERROR_LOG_FILE):
        log_with_timestamp(f"Bazı dosyalarda hatalar oluştu. Detaylar için '{ERROR_LOG_FILE}' dosyasına bakınız.")

if __name__ == "__main__":
    main()

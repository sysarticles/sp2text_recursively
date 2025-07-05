import os
import speech_recognition as sr
from pydub import AudioSegment

# --- AYARLAR ---
# Ana klasörünüzün yolunu buraya yapıştırın.
# Örnek Windows: "C:\\Users\\Kullanici\\Desktop\\SesDosyalarim"
# Örnek macOS/Linux: "/Users/kullanici/Desktop/SesDosyalarim"
ROOT_FOLDER = "BURAYA_ANA_KLASOR_YOLUNU_YAPISTIRIN"

# Tüm .txt dosyalarının kaydedileceği klasörün adı.
# Bu klasör, betiğin çalıştığı dizinde oluşturulacaktır.
OUTPUT_FOLDER = "Cikti_Dosyalari"

# Hata günlüğü için dosya yolu
ERROR_LOG_FILE = "hatali_dosyalar.txt"

# --- YENİ AYAR: GÜNLÜK LİMİT ---
# Google API limitlerine takılmamak için bir çalıştırmada yapılacak maksimum istek sayısı.
# Bu sınıra ulaşıldığında betik duracaktır.
# Ertesi gün tekrar çalıştırdığınızda kaldığı yerden devam eder.
MAX_REQUESTS_PER_RUN = 450

def transcribe_audio(file_path, root_folder):
    """
    Verilen yoldaki bir ses dosyasını metne çevirir.
    Başarılı bir çeviri yaparsa True, aksi halde False döner.
    """
    # --- YENİ DOSYA ADI OLUŞTURMA MANTIĞI ---
    try:
        relative_path = os.path.relpath(file_path, root_folder)
        path_without_ext, _ = os.path.splitext(relative_path)
        new_filename_base = path_without_ext.replace(os.sep, '_')
        new_filename_txt = new_filename_base + ".txt"
        output_txt_path = os.path.join(OUTPUT_FOLDER, new_filename_txt)
    except Exception as e:
        print(f"   [HATA] Dosya yolu oluşturulurken hata: {e} - Dosya: {file_path}")
        log_error(f"Dosya yolu hatası: {e} - Dosya: {file_path}")
        return False

    # Eğer metin dosyası zaten varsa, bu adımı atla ve False dön
    if os.path.exists(output_txt_path):
        print(f"-> Zaten mevcut, atlanıyor: {os.path.basename(output_txt_path)}")
        return False

    print(f"-> İşleniyor: {os.path.basename(file_path)}")

    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.m4a':
            sound = AudioSegment.from_file(file_path, format="m4a")
        else:
            sound = AudioSegment.from_file(file_path)
        
        temp_wav_path = "temp_audio.wav"
        sound.export(temp_wav_path, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="tr-TR")

        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"   [BAŞARILI] -> {os.path.basename(output_txt_path)} oluşturuldu.")
        return True # Başarılı oldu, True dön

    except sr.UnknownValueError:
        error_message = f"Google Speech Recognition konuşmayı anlayamadı: {file_path}"
        print(f"   [HATA] -> {error_message}")
        log_error(error_message)
        return False
    except sr.RequestError as e:
        error_message = f"Google Speech Recognition servisinden sonuç alınamadı; {e}: {file_path}"
        print(f"   [HATA] -> {error_message}")
        log_error(error_message)
        return False
    except Exception as e:
        error_message = f"Beklenmedik bir hata oluştu: {e}: {file_path}"
        print(f"   [HATA] -> {error_message}")
        log_error(error_message)
        return False
    finally:
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")

def log_error(message):
    """Hata mesajlarını bir dosyaya kaydeder."""
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def main():
    """
    Ana fonksiyon. Belirtilen klasörde gezinir ve ses dosyalarını işler.
    İstek limitine ulaşıldığında durur.
    """
    if ROOT_FOLDER == "BURAYA_ANA_KLASOR_YOLUNU_YAPISTIRIN" or not os.path.isdir(ROOT_FOLDER):
        print("Lütfen betik içerisindeki ROOT_FOLDER değişkenini geçerli bir klasör yolu ile güncelleyin.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        try:
            os.makedirs(OUTPUT_FOLDER)
            print(f"'{OUTPUT_FOLDER}' adında çıktı klasörü oluşturuldu.")
        except Exception as e:
            print(f"Çıktı klasörü oluşturulamadı: {e}")
            return

    print(f"'{ROOT_FOLDER}' klasörü ve alt klasörleri taranıyor...")
    print(f"Bu oturum için maksimum istek limiti: {MAX_REQUESTS_PER_RUN}")
    
    # --- YENİ: İstek sayacı ve limit kontrolü ---
    requests_count = 0
    limit_reached = False

    for dirpath, _, filenames in os.walk(ROOT_FOLDER):
        for filename in filenames:
            if filename.lower().endswith((".mp3", ".m4a")):
                full_path = os.path.join(dirpath, filename)
                
                # transcribe_audio fonksiyonu başarı durumunu döner
                was_successful = transcribe_audio(full_path, ROOT_FOLDER)
                
                if was_successful:
                    requests_count += 1
                    print(f"   --> Güncel istek sayısı: {requests_count}/{MAX_REQUESTS_PER_RUN}")
                
                # Limite ulaşıldı mı diye kontrol et
                if requests_count >= MAX_REQUESTS_PER_RUN:
                    print("\n----------------------------------------------------")
                    print(f"MAKSİMUM İSTEK LİMİTİNE ({MAX_REQUESTS_PER_RUN}) ULAŞILDI.")
                    print("API limitlerine takılmamak için betik durduruluyor.")
                    print("Yarın tekrar çalıştırarak kaldığınız yerden devam edebilirsiniz.")
                    print("----------------------------------------------------")
                    limit_reached = True
                    break # İç döngüden çık
        
        if limit_reached:
            break # Dış döngüden de çık

    if not limit_reached:
        print("\nİşlem tamamlandı.")

    if os.path.exists(ERROR_LOG_FILE):
        print(f"Bazı dosyalarda hatalar oluştu. Detaylar için '{ERROR_LOG_FILE}' dosyasına bakınız.")

if __name__ == "__main__":
    main()

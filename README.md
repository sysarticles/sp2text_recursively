# sp2text_recursively
convert audio files to text recuresively

pydub: .m4a ve .mp3 gibi farklı ses formatlarını işleyebilmek için.


OpenAI Whisper ile offline olarak çalışmak için:

Adım 1: Gerekli Kurulumlar
Önceki kurulumlarınıza ek olarak openai-whisper kütüphanesini kurmamız gerekiyor. pydub kütüphanesine artık ihtiyacımız kalmayacak.

FFmpeg'in Kurulu Olduğundan Emin Olun: Bu program, ses dosyalarını işlemek için hala gerekli. Eğer daha önce kurduysanız bu adımı atlayabilirsiniz.

Python Kütüphanelerini Kurun/Güncelleyin: Terminal veya komut istemcisini açın ve aşağıdaki komutu çalıştırın. Bu komut, Whisper kütüphanesini kuracaktır.

Bash

pip install SpeechRecognition openai-whisper
Not: Eğer daha önce pydub kurduysanız, sisteminizde kalmasının bir zararı yoktur, ancak bu betik artık onu kullanmayacak.

Adım 2: Güncellenmiş Python Betiği
Aşağıdaki kod, recognize_google yerine recognize_whisper kullanacak şekilde tamamen güncellenmiştir. Ayrıca, limit kontrolü gibi artık gereksiz olan kısımlar temizlenmiştir.

Kodu kopyalayıp mevcut ses_desifre_et.py dosyanızın içeriğiyle değiştirmeniz yeterlidir.

Adım 3: İlk Çalıştırma ve Model Seçimi
Model İndirme: Betiği ilk kez çalıştırdığınızda, Whisper seçtiğiniz modeli (WHISPER_MODEL = "base") internetten indirecektir. Bu işlem bir defaya mahsus yapılır ve modelin boyutuna göre biraz zaman alabilir. Lütfen sabırla bekleyin. İndirme tamamlandıktan sonraki çalıştırmalarınızda bu bekleme olmayacaktır.

Model Seçimi: Kodun başındaki WHISPER_MODEL değişkenini değiştirerek farklı modeller deneyebilirsiniz.

"tiny", "base": En hızlı olanlar ama doğrulukları daha düşük olabilir.

"small": Hız ve doğruluk arasında iyi bir denge sunar. Genellikle tavsiye edilir.

"medium", "large": En doğru sonuçları verirler ancak bilgisayarınızı oldukça yorabilir ve işlem süresini uzatabilirler.

Adım 4: Betiği Çalıştırma
Her şey hazır olduğunda, önceki gibi terminal üzerinden betiğinizi çalıştırabilirsiniz:


GOOGLE ile limitli sayıda az dosya çevirmek için:

SpeechRecognition: Ses dosyalarını metne dönüştürmek için (arka planda Google Speech Recognition API'ını kullanacağız).

Aşağıda, bu işlevi yerine getiren, adım adım açıklamaları ve kurulum talimatlarını içeren bir Python betiği bulunmaktadır.

Adım 1: Gerekli Kurulumlar
Bu betiği çalıştırmadan önce sisteminizde bazı programların ve Python kütüphanelerinin kurulu olması gerekmektedir.

FFmpeg Kurulumu: pydub kütüphanesinin .m4a ve .mp3 dosyalarını okuyabilmesi için FFmpeg adlı programa ihtiyacı vardır.

Windows: FFmpeg'i buradan indirip kurun ve sistem PATH'inize ekleyin.

macOS (Homebrew ile): brew install ffmpeg

Linux (apt ile): sudo apt update && sudo apt install ffmpeg

Python Kütüphanelerinin Kurulumu: Terminal veya komut istemcisine aşağıdaki komutları yazarak gerekli Python kütüphanelerini kurun:

Bash

pip install pydub SpeechRecognition



Kurulum ve Hazırlık Adımları
Bu güncellenmiş betiği çalıştırmadan önce yapmanız gereken iki basit adım var:

1. Gerekli Kütüphaneyi Kurun

Ayarları .env dosyasından okuyabilmek için python-dotenv kütüphanesine ihtiyacımız var. Terminal veya komut istemcisini açıp aşağıdaki komutu çalıştırın:

pip install python-dotenv

2. .env Dosyasını Oluşturun

Python betiğinizin (ses_desifre_et.py) bulunduğu ana dizine gidin ve  .env adında yeni bir metin dosyası oluşturun. Bu dosyanın içine, aşağıdaki gibi, kendi klasör yollarınızı belirterek ayarları yazın:

# Ses dosyalarınızın bulunduğu ana klasörün tam yolu
ROOT_FOLDER="C:\Users\user\Desktop\SesArsivim"

# Çıktıların kaydedileceği klasörün adı (bu klasör betik yanında oluşturulur)
OUTPUT_FOLDER="Desifre_Metinleri"

Önemli Notlar:

Windows'ta klasör yollarını yazarken \ karakterini kullanın.

Değişkenlerin etrafına tırnak işareti koymak, boşluk içeren yollarda sorun yaşamamanızı sağlar.

.env dosyasını kaydettikten sonra betiği çalıştırabilirsiniz. Betik, ayarları otomatik olarak bu dosyadan alacaktır.
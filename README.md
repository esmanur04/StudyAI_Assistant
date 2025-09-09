Yapay Zeka Tabanlı Çalışma Asistanı
StudyAI Assistant, öğrencilerin ve araştırmacıların çalışma süreçlerini verimli hale getirmek için tasarlanmış bir yapay zeka destekli projedir. Bu proje, farklı öğrenme ihtiyaçlarına cevap verebilen modüllerden oluşur.

Temel Özellikler
Soru-Cevap Modülü: Metin tabanlı verilerden, bir PDF dosyasından veya bir YouTube videosundan belirli konular hakkında sorular sormanızı ve hızlı yanıtlar almanızı sağlar.

Özet Çıkarma: Uzun metinleri, makaleleri veya ders notlarını ana fikirleri koruyarak özetler ve size sunar.

Flashcard Oluşturma: Belirlediğiniz konular veya metinler üzerinden otomatik olarak flashcard'lar (bilgi kartları) hazırlar. Bu kartlar, öğrenmeyi pekiştirme ve tekrar yapma süreçlerinde size yardımcı olur.

Teknolojik Altyapı
Bu proje, modern yapay zeka ve makine öğrenmesi kütüphaneleri kullanılarak geliştirilmiştir.

Python: Projenin temel programlama dili.

LangChain: Büyük dil modellerini (LLMs) entegre etmek için kullanılan bir framework. Bu sayede, karmaşık görevler kolayca yönetilir.

Streamlit: Projenin kullanıcı dostu ve interaktif arayüzünü oluşturmak için kullanılır.

Kurulum ve Kullanım
Projenin yerel makinenizde çalıştırılabilmesi için aşağıdaki adımları izleyin:

Depoyu Klonlayın:

Bash

git clone https://github.com/esmanur04/StudyAI_Assistant.git
cd StudyAI_Assistant
Sanal Ortam Oluşturun ve Aktif Edin:

Bash

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Gerekli Kütüphaneleri Yükleyin:

Bash

pip install -r requirements.txt
OpenAI API Anahtarınızı Tanımlayın:
Bir .env dosyası oluşturun ve OpenAI API anahtarınızı aşağıdaki gibi ekleyin.

OPENAI_API_KEY="sk-..."
Uygulamayı Çalıştırın:

Bash

streamlit run app.py
Katkıda Bulunma
Projeye katkıda bulunmak isterseniz, lütfen bir pull request gönderin veya bir issue açın. Her türlü geri bildirim ve katkı memnuniyetle karşılanır.

İletişim
Sorularınız veya önerileriniz için esmanur04@github.com adresine e-posta gönderebilirsiniz.

Lisans: Bu proje MIT Lisansı ile yayınlanmıştır. Daha fazla bilgi için LICENSE dosyasına göz atabilirsiniz.

# 📊 DataInsight Platform

### Interactive Data Analysis & Automated Reporting Platform

**DataInsight Platform**, CSV ve Excel dosyalarını yükleyerek veri temizleme, keşifsel veri analizi, istatistiksel analiz, görselleştirme ve otomatik raporlama işlemlerini tek bir Streamlit uygulaması altında gerçekleştiren bir veri analiz platformudur.

> **Upload • Clean • Analyze • Visualize • Report**

---

## 🚀 Proje Hakkında

Veri analizi sürecinde dosyanın okunmasından raporun oluşturulmasına kadar birçok işlem farklı araçlarda gerçekleştirilebiliyor.

Bu proje, bu süreci tek bir platformda birleştirmek amacıyla geliştirilmiştir.

Kullanıcı yalnızca **CSV veya Excel dosyasını yükler**. Platform;

* veriyi okur,
* temel veri temizleme işlemlerini gerçekleştirir,
* eksik verileri analiz eder,
* aykırı değerleri tespit eder,
* korelasyonları inceler,
* otomatik grafikler oluşturur,
* temel istatistikleri hesaplar,
* analiz sonuçlarını PDF ve Excel raporlarına dönüştürür.

---

## ✨ Özellikler

### 📂 Veri Yükleme

Desteklenen dosya formatları:

* CSV
* XLSX
* XLS

CSV dosyalarında farklı encoding ve ayraç formatları otomatik olarak denenir.

---

### 🧹 Otomatik Veri Temizleme

Platform veri yüklenirken çeşitli temizlik işlemlerini otomatik olarak gerçekleştirir:

* Boş satırların kaldırılması
* Tamamen boş sütunların kaldırılması
* Sütun isimlerinin temizlenmesi
* Metin alanlarındaki gereksiz boşlukların kaldırılması
* Duplicate kayıtların tespit edilmesi ve kaldırılması
* Sayısal görünen metinlerin sayısal değerlere dönüştürülmesi
* Tarih alanlarının otomatik olarak algılanması

Yapılan işlemler ayrıca kullanıcıya **temizleme günlüğü** olarak gösterilir.

---

### ❓ Eksik Veri Analizi

Eksik değerler sütun bazında analiz edilir.

Kullanıcı aşağıdaki stratejilerden birini seçebilir:

* Değişiklik yapma
* Satırları sil
* Ortalama ile doldur
* Medyan ile doldur
* Mod ile doldur
* Önceki değerle doldur
* Sıfır ile doldur

Eksik değerlerin dağılımı grafik üzerinde de gösterilir.

---

### 🎯 Aykırı Değer Analizi

Sayısal değişkenlerde aykırı değerleri tespit etmek için iki farklı yöntem kullanılabilir:

* **IQR (Interquartile Range)**
* **Z-Score**

Ayrıca seçilen değişkenler için **Boxplot** görselleştirmeleri oluşturulur.

---

### 🔗 Korelasyon Analizi

Sayısal değişkenler arasındaki ilişkiler farklı korelasyon yöntemleriyle incelenebilir:

* Pearson
* Spearman
* Kendall

Korelasyon matrisi heatmap olarak görselleştirilir.

Ayrıca belirlenen korelasyon eşiğinin üzerindeki güçlü ilişkiler otomatik olarak listelenir.

---

### 📈 Veri Görselleştirme

Platform veri setinin yapısına göre otomatik grafikler oluşturabilir.

Desteklenen görselleştirmeler:

* Histogram
* KDE dağılım grafikleri
* Bar chart
* Boxplot
* Scatter plot
* Korelasyon heatmap

Bunun yanında kullanıcı manuel olarak değişken seçerek grafik oluşturabilir.

---

### 📐 İstatistiksel Analiz

Sayısal değişkenler için:

* Ortalama
* Medyan
* Standart sapma
* Minimum
* Maksimum
* %25 çeyrek
* %75 çeyrek
* Çarpıklık
* Basıklık

gibi temel istatistikler hesaplanır.

Kategorik değişkenler için de:

* Benzersiz değer sayısı
* En sık görülen değer
* Frekans bilgileri

sunulur.

---

## 📄 Otomatik Raporlama

Analiz sonuçları iki farklı formatta dışa aktarılabilir.

### PDF Raporu

PDF içerisinde analiz sonuçları, istatistikler, aykırı değerler, korelasyonlar ve oluşturulan grafikler yer alır.

### Excel Raporu

Excel raporu birden fazla çalışma sayfası içerir ve analiz sonuçlarını daha detaylı şekilde incelemeye olanak sağlar.

---

## 🏗️ Proje Mimarisi

```text
DataInsight-Platform/
│
├── app.py
│
├── modules/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── data_cleaner.py
│   ├── report_generator.py
│   └── visualizer.py
│
├── fonts/
│   ├── DejaVuSans.ttf
│   └── DejaVuSans-Bold.ttf
│
├── ornek_veri_seti.csv
├── requirements.txt
└── README.md
```

---

## 🔄 Veri Analizi Akışı

```text
CSV / Excel
     │
     ▼
Data Loading
     │
     ▼
Data Cleaning
     │
     ├── Missing Values
     ├── Duplicate Records
     ├── Data Types
     └── Date Detection
     │
     ▼
Exploratory Data Analysis
     │
     ├── Statistics
     ├── Outliers
     ├── Correlation
     └── Categorical Analysis
     │
     ▼
Visualization
     │
     ├── Histogram
     ├── Boxplot
     ├── Scatter Plot
     └── Heatmap
     │
     ▼
Automated Reporting
     │
     ├── PDF
     └── Excel
```

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji  | Kullanım Alanı                      |
| ---------- | ----------------------------------- |
| Python     | Ana programlama dili                |
| Streamlit  | Web uygulaması ve kullanıcı arayüzü |
| Pandas     | Veri işleme ve analiz               |
| NumPy      | Sayısal hesaplamalar                |
| SciPy      | İstatistiksel analiz                |
| Matplotlib | Veri görselleştirme                 |
| Seaborn    | İleri veri görselleştirme           |
| OpenPyXL   | Excel işlemleri                     |
| XlsxWriter | Excel raporları                     |
| ReportLab  | PDF raporları                       |

---

## 💻 Kurulum

Projeyi bilgisayarınıza klonlayın:

```bash
git clone https://github.com/USERNAME/DataInsight-Platform.git
```

Proje klasörüne girin:

```bash
cd DataInsight-Platform
```

Sanal ortam oluşturmanız önerilir:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

---

## ▶️ Uygulamayı Çalıştırma

Streamlit uygulamasını başlatmak için:

```bash
streamlit run app.py
```

Tarayıcıda açılan uygulamaya CSV veya Excel dosyanızı yükleyerek analize başlayabilirsiniz.

---

## 📊 Örnek Veri Seti

Projede uygulamayı test etmek amacıyla:

```text
ornek_veri_seti.csv
```

dosyası bulunmaktadır.

Bu veri seti kullanılarak veri temizleme, eksik değer analizi, aykırı değer tespiti, korelasyon analizi ve grafik üretimi test edilebilir.

---

## 🎯 Projenin Amacı

Bu projenin temel amacı yalnızca grafik üretmek değil, veri analiz sürecinin farklı aşamalarını tek bir uygulamada bir araya getirmektir.

Platform;

**Veri → Temizleme → Analiz → Görselleştirme → Raporlama**

akışını takip ederek kullanıcıya uçtan uca bir analiz deneyimi sunmayı hedeflemektedir.

---

## 🔮 Gelecekte Eklenebilecek Özellikler

* [ ] Otomatik EDA özeti
* [ ] Makine öğrenmesi modelleri
* [ ] Feature engineering modülü
* [ ] Model performans karşılaştırması
* [ ] Otomatik insight/recommendation sistemi
* [ ] Daha gelişmiş dashboard
* [ ] SQL veri kaynağı desteği
* [ ] API üzerinden veri alma
* [ ] Büyük veri setleri için optimizasyon
* [ ] Kullanıcı bazlı proje geçmişi
* [ ] Streamlit Cloud deployment
* [ ] Daha gelişmiş PDF tasarımı

---

## 👩‍💻 Geliştirici

**Sakine Cansu Topci**

Yönetim Bilişim Sistemleri mezunu.

Bu proje; Python, Pandas, veri analizi, veri görselleştirme ve Streamlit kullanılarak geliştirilmiştir.

---

## 📌 Proje Türü

**Data Analysis • Exploratory Data Analysis • Data Visualization • Streamlit • Automated Reporting**

---

⭐ Projeyi faydalı bulduysanız repository'yi yıldızlamayı unutmayın!

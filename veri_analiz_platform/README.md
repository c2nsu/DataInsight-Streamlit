# 📊 Veri Analizi & Otomatik Raporlama Platformu

CSV veya Excel dosyanızı yükleyin; platform verinizi otomatik olarak temizler, eksik veri ve aykırı değerleri tespit eder, korelasyon analizi yapar, grafikler üretir ve tek tıkla profesyonel bir **PDF** veya **Excel** raporu indirmenizi sağlar.

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 📁 Dosya Yükleme | CSV (otomatik encoding/ayraç tespiti) ve Excel (.xlsx/.xls) desteği |
| 🧹 Otomatik Veri Temizleme | Boş satır/sütun temizliği, boşluk kırpma, tekrar kaldırma, sayı/tarih tipi tespiti |
| ❓ Eksik Veri Analizi | Sütun bazında eksik oran raporu + doldurma stratejileri (ortalama, medyan, mod, ffill, satır silme) |
| 🎯 Aykırı Değer Tespiti | IQR ve Z-Score yöntemleri, boxplot görselleştirme |
| 🔗 Korelasyon Analizi | Pearson/Spearman/Kendall, ısı haritası, güçlü ilişki listesi |
| 📈 Otomatik Grafikler | Dağılım, frekans ve ilişki grafiklerinin otomatik seçimi |
| 📐 Temel İstatistikler | Ortalama, medyan, std, çarpıklık, basıklık ve daha fazlası |
| 📥 Rapor İndirme | Görsellerle zenginleştirilmiş PDF + çok sayfalı Excel raporu |

## 🚀 Kurulum ve Çalıştırma

```bash
# Bağımlılıkları kurun
pip install -r requirements.txt

# Uygulamayı başlatın
streamlit run app.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` açılacaktır.

## 🗂️ Proje Yapısı

```
veri_analiz_platform/
├── app.py                      # Streamlit ana uygulaması (UI)
├── modules/
│   ├── data_cleaner.py         # Dosya yükleme + otomatik temizlik
│   ├── analyzer.py             # Aykırı değer, korelasyon, istatistik hesapları
│   ├── visualizer.py           # Matplotlib/Seaborn grafik üretimi
│   └── report_generator.py     # PDF (ReportLab) ve Excel (XlsxWriter) rapor motoru
├── requirements.txt
└── README.md
```

## 🖥️ Ekranlar

Uygulama 7 sekmeden oluşur:
1. **Genel Bakış & Temizlik** — veri seti özeti ve uygulanan otomatik temizlik adımları
2. **Eksik Veri** — eksik veri tablosu ve görseli
3. **Aykırı Değerler** — IQR/Z-Score analizleri ve boxplot
4. **Korelasyon** — ısı haritası ve güçlü ilişki tablosu
5. **Grafikler** — otomatik + manuel grafik oluşturma
6. **İstatistikler** — sayısal ve kategorik özet tablolar
7. **Rapor İndir** — PDF ve Excel rapor üretimi

## 🛠️ Kullanılan Teknolojiler

- **Streamlit** — arayüz
- **Pandas / NumPy** — veri işleme
- **SciPy** — istatistiksel hesaplamalar (Z-score)
- **Matplotlib / Seaborn** — görselleştirme
- **ReportLab** — PDF rapor üretimi (Türkçe karakter desteği için DejaVu Sans fontu gömülüdür)
- **XlsxWriter** — çok sayfalı, biçimlendirilmiş Excel rapor üretimi

## 📌 Notlar / Geliştirme Fikirleri

- Şu an desteklenen dosya boyutu Streamlit'in varsayılan yükleme limitine (200MB) bağlıdır; `.streamlit/config.toml` üzerinden artırılabilir.
- Docker imajı hazırlanarak (`Dockerfile`) veya Streamlit Community Cloud'a deploy edilerek canlıya alınabilir — portföyde canlı link paylaşmak için idealdir.
- İleri seviye geliştirme fikirleri: çoklu dosya karşılaştırma, otomatik makine öğrenmesi (AutoML) önerileri, zaman serisi analizi modülü.

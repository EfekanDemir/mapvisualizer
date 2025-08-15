# Excel'den İnteraktif Harita Oluşturucu

Bu Python betiği, Excel dosyalarından gelişmiş ve interaktif haritalar oluşturur. Profesyonel görünüm, akıllı renklendirme ve kullanıcı dostu arayüz sunar.

## 🚀 Özellikler

- **Otomatik Dosya Tespiti**: Çalışma dizinindeki tüm Excel dosyalarını bulur
- **Akıllı Veri Temizliği**: Geçersiz koordinatları otomatik temizler
- **Google Places API Entegrasyonu**: 🆕 Konumlar için otomatik zenginleştirme
  - 📸 Fotoğraflar
  - ⭐ Puanlamalar ve değerlendirme sayıları
  - 📍 Detaylı adres bilgileri
  - 📞 Telefon numaraları
  - 🌐 Resmi web siteleri
  - 🕒 Açılış saatleri
  - 💰 Fiyat seviyesi
- **Dinamik Renk Skalası**: Rank değerlerine göre yeşilden mora geçişli renklendirme
- **Özel Pin Tasarımı**: Rank değerini gösteren özel tasarımlı pinler
- **Tıklanabilir Linkler**: URL sütunundaki linkleri popup'larda gösterir
- **Marker Clustering**: Yakın konumları akıllı gruplar halinde organize eder
- **Çoklu Harita Stilleri**: OpenStreetMap, CartoDB Positron ve Dark Matter
- **Tam Ekran Modu**: Haritayı tam ekranda görüntüleme
- **Otomatik Tarayıcı Açma**: Harita oluşturulduktan sonra otomatik açılır

## 📋 Gereksinimler

### Zorunlu Sütunlar
- `latitude`: Enlem (sayısal)
- `longitude`: Boylam (sayısal) 
- `title`: Konum başlığı (metin)

### Opsiyonel Sütunlar
- `rank`: Sıralama değeri (sayısal veya özel değer)
- `url`: Web sitesi linki (metin)

### Google Places API (Opsiyonel)
- API Key gereklidir (Google Cloud Console'dan alınabilir)
- Places API aktifleştirilmiş olmalıdır
- Kullanıldığında konum bilgileri otomatik zenginleştirilir

## 🎨 Pin Renklendirme Kuralları

1. **Özel Değer ("20+")**: `%26%2310006%3B` değeri → Kırmızı pin, "20+" metni
2. **Boş Değer**: Rank yoksa → Standart mavi pin
3. **Sayısal Değer**: 1-10 arası → Yeşilden mora gradient renk

## 🛠️ Kurulum ve Çalıştırma

### Otomatik Kurulum (Önerilen)

**Windows kullanıcıları için:**
```cmd
excel_to_map.bat
```

**Linux/macOS kullanıcıları için:**
```bash
./excel_to_map.sh
```

Bu batch/script dosyaları otomatik olarak:
- Python kurulumunu kontrol eder
- Gerekli paketleri kurar
- Excel dosyalarını kontrol eder
- Harita oluşturucuyu çalıştırır

### Manuel Kurulum

1. Gerekli paketleri kurun:
```bash
pip install -r requirements.txt
```

2. Betiği çalıştırın:
```bash
python excel_to_map.py
```

## 📊 Kullanım

1. Excel dosyalarınızı betik ile aynı klasöre koyun
2. Betiği çalıştırın: `python excel_to_map.py`
3. Listeden bir Excel dosyası seçin
4. Harita otomatik olarak oluşturulup tarayıcıda açılır

## 📁 Çıktı

- `[dosya_adı]_harita.html`: İnteraktif HTML haritası
- Otomatik tarayıcı açılımı
- Konum sayısı ve işlem durumu raporu

## 🔧 Teknik Detaylar

- **Harita Merkezi**: Tüm noktaları kapsayacak şekilde otomatik hesaplanır
- **Zoom Seviyesi**: Noktaların dağılımına göre akıllı ayarlanır
- **Marker Clustering**: folium MarkerCluster plugin'i kullanır
- **Renk Interpolasyonu**: RGB doğrusal geçiş hesaplama
- **Popup İçeriği**: HTML formatında zengin içerik

## 📝 Örnek Veri Formatı

| latitude | longitude | title | rank | url |
|----------|-----------|-------|------|-----|
| 39.9334 | 32.8597 | Ankara | 1 | https://example.com |
| 40.7829 | -73.9654 | New York | 5 | https://nyc.gov |
| 41.0082 | 28.9784 | İstanbul | %26%2310006%3B | |

## ⚡ Performans

- Büyük veri setleri için marker clustering
- Verimli renk hesaplama algoritması
- Hafıza dostu veri işleme
- Hızlı HTML çıktı üretimi

## 📁 Dosyalar

- **`excel_to_map.py`** - Ana Python betiği (Google Places API entegrasyonu ile)
- **`excel_to_map.bat`** - Windows batch dosyası (otomatik kurulum)
- **`excel_to_map.sh`** - Linux/macOS bash script (otomatik kurulum)
- **`requirements.txt`** - Python paket gereksinimleri (googlemaps dahil)
- **`README.md`** - Bu kılavuz

## 🔧 Batch/Script Dosyaları Özellikleri

### Windows (.bat)
- ✅ Python kurulum kontrolü
- ✅ pip kurulum kontrolü  
- ✅ Paket kurulum kontrolü ve otomatik kurulum
- ✅ Excel dosya kontrolü
- ✅ UTF-8 karakter desteği
- ✅ Renkli çıktı
- ✅ Detaylı hata mesajları

### Linux/macOS (.sh)
- ✅ Python3/python otomatik algılama
- ✅ Sanal ortam desteği
- ✅ Sistem paket yöneticisi entegrasyonu
- ✅ ANSI renk kodları
- ✅ Unicode emoji desteği
- ✅ Kapsamlı hata yönetimi

## 🗝️ Google Places API Kullanımı

### API Key Alma
1. [Google Cloud Console](https://console.cloud.google.com/)'a gidin
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. **APIs & Services > Library** bölümünde **Places API**'yi aktifleştirin
4. **APIs & Services > Credentials** bölümünde API key oluşturun
5. API key'i güvenlik için kısıtlayın (domain/IP bazlı)

### Maliyet
- **Places API**: İlk 200$ ücretsiz kredi (aylık)
- **Nearby Search**: $17/1000 request sonrası
- **Place Details**: $17/1000 request sonrası
- **Photos**: $7/1000 request sonrası

### Kullanım
API key'i `excel_to_map.py` dosyasının başında güncelleyin:
```python
# Line 47: self.google_api_key = "YOUR_API_KEY_HERE"
```

Veya script çalıştırırken parametre olarak geçin:
```python
converter = ExcelToMapConverter(google_api_key="YOUR_API_KEY")
```

### Özellikler
- ✅ Otomatik konum tanıma
- ✅ Fotoğraf entegrasyonu  
- ✅ Gerçek zamanlı açılış saatleri
- ✅ Kullanıcı puanlamaları
- ✅ İletişim bilgileri
- ✅ Rate limiting koruması

## 🤝 Destek

Herhangi bir sorun için betik detaylı hata mesajları sağlar ve güvenli bir şekilde sonlanır.
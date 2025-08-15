# Excel'den İnteraktif Harita Oluşturucu

Bu Python betiği, Excel dosyalarından gelişmiş ve interaktif haritalar oluşturur. Profesyonel görünüm, akıllı renklendirme ve kullanıcı dostu arayüz sunar.

## 🚀 Özellikler

- **Otomatik Dosya Tespiti**: Çalışma dizinindeki tüm Excel dosyalarını bulur
- **Akıllı Veri Temizliği**: Geçersiz koordinatları otomatik temizler
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

## 🎨 Pin Renklendirme Kuralları

1. **Özel Değer ("20+")**: `%26%2310006%3B` değeri → Kırmızı pin, "20+" metni
2. **Boş Değer**: Rank yoksa → Standart mavi pin
3. **Sayısal Değer**: 1-10 arası → Yeşilden mora gradient renk

## 🛠️ Kurulum

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

## 🤝 Destek

Herhangi bir sorun için betik detaylı hata mesajları sağlar ve güvenli bir şekilde sonlanır.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel'den Gelişmiş İnteraktif Harita Oluşturucu
================================================

Bu betik Excel dosyalarından veri okuyarak profesyonel ve interaktif 
haritalar oluşturur. Özellikler:
- Otomatik dosya tespiti ve seçimi
- Akıllı veri temizliği
- Dinamik renk skalası (yeşilden mora)
- Tıklanabilir linkler
- Marker clustering
- Otomatik tarayıcı açma

Gerekli sütunlar: latitude, longitude, title
Opsiyonel sütunlar: rank, url

Yazar: Python Geliştirici
"""

import os
import sys
import glob
import webbrowser
from pathlib import Path
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import googlemaps
import requests
import time
from urllib.parse import quote


class ExcelToMapConverter:
    """Excel dosyalarından interaktif harita oluşturan ana sınıf"""
    
    def __init__(self, google_api_key: str = None):
        self.required_columns = ['latitude', 'longitude', 'title']
        self.optional_columns = ['rank', 'url']
        self.special_rank_value = "%26%2310006%3B"
        self.color_green = "#5cb85c"
        self.color_purple = "#5e35b1"
        self.color_red = "#d9534f"
        self.color_gray = "#6c757d"
        
        # Google Places API setup
        self.google_api_key = google_api_key or "AIzaSyDbxLE2AXm9ZhryXpuWpBz8LDlDnBc9-9Y"
        if self.google_api_key:
            try:
                self.gmaps = googlemaps.Client(key=self.google_api_key)
                self.places_enabled = True
                print("✅ Google Places API bağlantısı kuruldu")
            except Exception as e:
                print(f"⚠️ Google Places API bağlantısı kurulamadı: {e}")
                self.places_enabled = False
                self.gmaps = None
        else:
            self.places_enabled = False
            self.gmaps = None
        
    def find_excel_files(self, directory: str = ".") -> List[str]:
        """Belirtilen dizindeki Excel dosyalarını bulur"""
        excel_pattern = os.path.join(directory, "*.xlsx")
        excel_files = glob.glob(excel_pattern)
        
        # Sadece dosya adlarını döndür
        return [os.path.basename(f) for f in excel_files]
    
    def select_excel_file(self) -> str:
        """Kullanıcıdan Excel dosyası seçmesini ister"""
        excel_files = self.find_excel_files()
        
        if not excel_files:
            print("❌ Bu dizinde .xlsx uzantılı dosya bulunamadı!")
            sys.exit(1)
        
        print("📊 Mevcut Excel dosyaları:")
        print("-" * 40)
        
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        print("-" * 40)
        
        while True:
            try:
                choice = input(f"\nLütfen bir dosya seçin (1-{len(excel_files)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(excel_files):
                    selected_file = excel_files[choice_num - 1]
                    print(f"✅ Seçilen dosya: {selected_file}")
                    return selected_file
                else:
                    print(f"❌ Lütfen 1-{len(excel_files)} arasında bir sayı girin!")
                    
            except ValueError:
                print("❌ Lütfen geçerli bir sayı girin!")
            except KeyboardInterrupt:
                print("\n\n👋 İşlem iptal edildi!")
                sys.exit(0)
    
    def validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Veriyi doğrular ve temizler"""
        print("🔍 Sütun kontrolü yapılıyor...")
        
        # Zorunlu sütunları kontrol et
        missing_required = [col for col in self.required_columns if col not in df.columns]
        if missing_required:
            print(f"❌ Zorunlu sütunlar eksik: {missing_required}")
            sys.exit(1)
        
        # Opsiyonel sütunları kontrol et
        available_optional = [col for col in self.optional_columns if col in df.columns]
        missing_optional = [col for col in self.optional_columns if col not in df.columns]
        
        if available_optional:
            print(f"✅ Bulunan opsiyonel sütunlar: {available_optional}")
        if missing_optional:
            print(f"ℹ️  Eksik opsiyonel sütunlar: {missing_optional} (atlanacak)")
        
        print(f"📝 Orijinal veri satır sayısı: {len(df)}")
        
        # Latitude ve longitude temizliği
        print("🧹 Koordinat verisi temizleniyor...")
        original_len = len(df)
        
        # Sayısal dönüşüm ve geçersiz değerleri temizle
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # NaN değerleri temizle
        df = df.dropna(subset=['latitude', 'longitude'])
        
        cleaned_len = len(df)
        removed_count = original_len - cleaned_len
        
        if removed_count > 0:
            print(f"⚠️  {removed_count} satır geçersiz koordinat nedeniyle temizlendi")
        
        print(f"✅ Temizlenen veri satır sayısı: {cleaned_len}")
        
        # Rank sütunu varsa temizle
        if 'rank' in df.columns:
            print("🔢 Rank verisi işleniyor...")
            
            # Özel değerleri koru, diğerlerini sayısal yapmaya çalış
            def clean_rank(value):
                if pd.isna(value):
                    return None
                if str(value) == self.special_rank_value:
                    return self.special_rank_value
                try:
                    return pd.to_numeric(value)
                except (ValueError, TypeError):
                    return value  # Dönüştürülemeyen değerleri olduğu gibi bırak
            
            df['rank'] = df['rank'].apply(clean_rank)
        
        return df
    
    def calculate_map_bounds(self, df: pd.DataFrame) -> Tuple[float, float, int]:
        """Harita sınırlarını hesaplar"""
        lats = df['latitude'].values
        lons = df['longitude'].values
        
        # Merkez noktası
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        
        # Yakınlaştırma seviyesi hesaplama
        lat_range = np.max(lats) - np.min(lats)
        lon_range = np.max(lons) - np.min(lons)
        max_range = max(lat_range, lon_range)
        
        # Yakınlaştırma seviyesi belirleme
        if max_range > 10:
            zoom = 6
        elif max_range > 5:
            zoom = 8
        elif max_range > 1:
            zoom = 10
        elif max_range > 0.5:
            zoom = 12
        else:
            zoom = 14
        
        return center_lat, center_lon, zoom
    
    def interpolate_color(self, value: float, min_val: float, max_val: float) -> str:
        """Yeşil-mor arası renk interpolasyonu"""
        if min_val == max_val:
            return self.color_green
        
        # Normalize et (0-1 arası)
        normalized = (value - min_val) / (max_val - min_val)
        
        # Yeşil RGB: (92, 184, 92)
        # Mor RGB: (94, 53, 177)
        green_rgb = (92, 184, 92)
        purple_rgb = (94, 53, 177)
        
        # Interpolasyon
        r = int(green_rgb[0] + (purple_rgb[0] - green_rgb[0]) * normalized)
        g = int(green_rgb[1] + (purple_rgb[1] - green_rgb[1]) * normalized)
        b = int(green_rgb[2] + (purple_rgb[2] - green_rgb[2]) * normalized)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def get_pin_properties(self, row: pd.Series, numeric_ranks: List[float]) -> Dict[str, Any]:
        """Pin özelliklerini belirler (renk, metin, tip)"""
        pin_props = {
            'color': '#007bff',  # Varsayılan mavi
            'text': '',
            'use_div_icon': False
        }
        
        if 'rank' not in row.index or pd.isna(row['rank']):
            # Kural 2: Boş değer - daire içinde "?" göster
            pin_props.update({
                'color': '#007bff',  # Mavi renk
                'text': '?',
                'use_div_icon': True
            })
            return pin_props
        
        rank_value = row['rank']
        
        # Kural 1: Özel değer kontrolü
        if str(rank_value) == self.special_rank_value:
            pin_props.update({
                'color': self.color_gray,
                'text': '20+',
                'use_div_icon': True
            })
            return pin_props
        
        # Kural 3: Sayısal değer kontrolü
        if isinstance(rank_value, (int, float)) and not pd.isna(rank_value):
            if numeric_ranks and len(numeric_ranks) > 1:
                min_rank = min(numeric_ranks)
                max_rank = max(numeric_ranks)
                color = self.interpolate_color(float(rank_value), min_rank, max_rank)
            else:
                color = self.color_green
            
            pin_props.update({
                'color': color,
                'text': str(int(rank_value)) if rank_value == int(rank_value) else str(rank_value),
                'use_div_icon': True
            })
            return pin_props
        
        # Varsayılan durum - sayısal olmayan rank değerleri için
        pin_props.update({
            'color': '#6c757d',  # Gri renk
            'text': str(rank_value)[:3] if len(str(rank_value)) > 3 else str(rank_value),  # Uzun metinleri kısalt
            'use_div_icon': True
        })
        return pin_props
    
    def create_custom_div_icon(self, text: str, color: str) -> folium.DivIcon:
        """Özel DivIcon oluşturur"""
        html = f"""
        <div style="
            background-color: {color};
            color: white;
            font-weight: bold;
            font-size: 12px;
            text-align: center;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            line-height: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            border: 2px solid white;
        ">{text}</div>
        """
        
        return folium.DivIcon(
            html=html,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    
    def get_places_info(self, lat: float, lon: float, name: str = None) -> Dict[str, Any]:
        """Google Places API'den konum bilgilerini alır"""
        if not self.places_enabled:
            return {}
        
        try:
            # Nearby search ile en yakın yeri bul
            nearby_search = self.gmaps.places_nearby(
                location=(lat, lon),
                radius=100,  # 100 metre yarıçap
                language='tr'
            )
            
            if not nearby_search.get('results'):
                return {}
            
            # En yakın sonucu al
            place = nearby_search['results'][0]
            place_id = place.get('place_id')
            
            if not place_id:
                return {}
            
            # Detaylı bilgi al
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'rating', 'formatted_phone_number', 'website', 
                       'opening_hours', 'photo', 'type', 'formatted_address',
                       'price_level', 'user_ratings_total'],
                language='tr'
            )
            
            result = place_details.get('result', {})
            
            # Fotoğraf URL'si oluştur
            photos = result.get('photo', [])
            photo_url = None
            if photos:
                photo_reference = photos[0].get('photo_reference')
                if photo_reference:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=300&photo_reference={photo_reference}&key={self.google_api_key}"
            
            return {
                'name': result.get('name', ''),
                'rating': result.get('rating'),
                'rating_count': result.get('user_ratings_total'),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'address': result.get('formatted_address', ''),
                'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'photo_url': photo_url,
                'types': result.get('type', []),
                'price_level': result.get('price_level')
            }
            
        except Exception as e:
            print(f"⚠️ Places API hatası ({lat}, {lon}): {e}")
            return {}
    
    def create_popup_content(self, row: pd.Series, places_info: Dict[str, Any] = None) -> str:
        """Popup içeriği oluşturur (Google Places bilgileri ile zenginleştirilmiş)"""
        title = row['title']
        content = f"<b>{title}</b>"
        
        # Google Places bilgileri varsa ekle
        if places_info:
            # Fotoğraf
            if places_info.get('photo_url'):
                content += f'<br><br><img src="{places_info["photo_url"]}" style="max-width: 280px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            
            # Rating
            if places_info.get('rating'):
                rating = places_info['rating']
                rating_count = places_info.get('rating_count', 0)
                stars = "⭐" * int(rating)
                content += f'<br><br><span style="color: #ff9800; font-weight: bold;">{stars} {rating}/5</span>'
                if rating_count:
                    content += f' <span style="color: #666; font-size: 12px;">({rating_count} değerlendirme)</span>'
            
            # Adres
            if places_info.get('address'):
                content += f'<br><br>📍 <span style="color: #555;">{places_info["address"]}</span>'
            
            # Telefon
            if places_info.get('phone'):
                content += f'<br>📞 <a href="tel:{places_info["phone"]}" style="color: #007bff; text-decoration: none;">{places_info["phone"]}</a>'
            
            # Website (Places API'den)
            if places_info.get('website'):
                content += f'<br>🌐 <a href="{places_info["website"]}" target="_blank" style="color: #007bff; text-decoration: none;">Website</a>'
            
            # Açılış saatleri (sadece bugün)
            opening_hours = places_info.get('opening_hours', [])
            if opening_hours:
                import datetime
                today = datetime.datetime.now().weekday()  # 0=Pazartesi, 6=Pazar
                if today < len(opening_hours):
                    content += f'<br>🕒 <span style="color: #555; font-size: 12px;">{opening_hours[today]}</span>'
            
            # Fiyat seviyesi
            price_level = places_info.get('price_level')
            if price_level is not None:
                price_symbols = "💰" * (price_level + 1) if price_level <= 3 else "💰💰💰💰"
                content += f'<br>💵 <span style="color: #4caf50;">{price_symbols}</span>'
        
        # Orijinal URL varsa ekle (Places API website'ından farklıysa)
        if 'url' in row.index and pd.notna(row['url']) and str(row['url']).strip():
            url = str(row['url']).strip()
            if url and not url.lower() in ['nan', 'none', '']:
                places_website = places_info.get('website', '') if places_info else ''
                if url != places_website:
                    content += f'<br><br><a href="{url}" target="_blank" style="color: #007bff; text-decoration: none;">🔗 Detayları Görüntüle</a>'
        
        return content
    
    def create_map(self, df: pd.DataFrame, output_filename: str) -> None:
        """İnteraktif harita oluşturur"""
        print("🗺️  Harita oluşturuluyor...")
        
        # Harita merkezi ve zoom hesapla
        center_lat, center_lon, zoom = self.calculate_map_bounds(df)
        
        # Harita oluştur
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Alternatif harita katmanları ekle
        folium.TileLayer('CartoDB Positron', name='CartoDB Positron').add_to(m)
        folium.TileLayer('CartoDB Dark_Matter', name='CartoDB Dark Matter').add_to(m)
        
        # Marker Cluster ekle
        marker_cluster = MarkerCluster(
            name="Konumlar",
            overlay=True,
            control=True
        ).add_to(m)
        
        # Sayısal rank değerlerini bul (renk skalası için)
        numeric_ranks = []
        if 'rank' in df.columns:
            for value in df['rank']:
                if isinstance(value, (int, float)) and not pd.isna(value):
                    numeric_ranks.append(float(value))
        
        print(f"📍 {len(df)} konum işleniyor...")
        if self.places_enabled:
            print("🔍 Google Places API ile konum bilgileri zenginleştiriliyor...")
        
        # Her satır için marker oluştur
        for idx, row in df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            
            # Google Places bilgilerini al (varsa)
            places_info = {}
            if self.places_enabled:
                places_info = self.get_places_info(lat, lon, row['title'])
                if places_info:
                    print(f"✅ Places bilgisi alındı: {row['title']}")
                else:
                    print(f"ℹ️  Places bilgisi bulunamadı: {row['title']}")
                # API rate limiting için kısa bekleme
                time.sleep(0.1)
            
            # Pin özelliklerini al
            pin_props = self.get_pin_properties(row, numeric_ranks)
            
            # Popup içeriği (Places bilgileri ile zenginleştirilmiş)
            popup_content = self.create_popup_content(row, places_info)
            
            # Marker oluştur
            if pin_props['use_div_icon'] and pin_props['text']:
                # Özel DivIcon kullan
                icon = self.create_custom_div_icon(pin_props['text'], pin_props['color'])
            else:
                # Standart icon kullan
                icon = folium.Icon(color='blue', icon='info-sign')
            
            # Tooltip için Places name varsa onu kullan
            tooltip_text = places_info.get('name', row['title']) if places_info else row['title']
            
            # Marker'ı cluster'a ekle
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=320),
                tooltip=tooltip_text,
                icon=icon
            ).add_to(marker_cluster)
        
        # Kontroller ekle
        folium.LayerControl().add_to(m)
        
        # Tam ekran plugin'i ekle
        from folium.plugins import Fullscreen
        Fullscreen().add_to(m)
        
        # Haritayı kaydet
        m.save(output_filename)
        print(f"✅ Harita başarıyla oluşturuldu: {output_filename}")
    
    def open_in_browser(self, filename: str) -> None:
        """Dosyayı varsayılan tarayıcıda açar"""
        try:
            file_path = os.path.abspath(filename)
            file_url = f"file://{file_path}"
            webbrowser.open(file_url)
            print(f"🌐 Harita tarayıcıda açıldı: {filename}")
        except Exception as e:
            print(f"⚠️  Tarayıcıda açılırken hata: {e}")
            print(f"📂 Manuel olarak açmak için: {os.path.abspath(filename)}")
    
    def run(self) -> None:
        """Ana çalıştırma fonksiyonu"""
        print("=" * 60)
        print("🗺️  EXCEL'DEN İNTERAKTİF HARİTA OLUŞTURUCU")
        print("=" * 60)
        
        try:
            # 1. Excel dosyası seç
            excel_file = self.select_excel_file()
            
            # 2. Veriyi oku
            print(f"\n📖 {excel_file} dosyası okunuyor...")
            df = pd.read_excel(excel_file)
            
            # 3. Veriyi doğrula ve temizle
            df = self.validate_and_clean_data(df)
            
            if len(df) == 0:
                print("❌ Temizleme sonrası hiç geçerli veri kalmadı!")
                return
            
            # 4. Çıktı dosya adı oluştur
            base_name = Path(excel_file).stem
            output_filename = f"{base_name}_harita.html"
            
            # 5. Harita oluştur
            self.create_map(df, output_filename)
            
            # 6. Başarı mesajı ve tarayıcıda aç
            print("\n" + "=" * 60)
            print("🎉 HARİTANIZ BAŞARIYLA OLUŞTURULDU!")
            print("=" * 60)
            print(f"📂 Dosya: {output_filename}")
            print(f"📊 İşlenen konum sayısı: {len(df)}")
            
            self.open_in_browser(output_filename)
            
        except FileNotFoundError:
            print("❌ Dosya bulunamadı!")
        except pd.errors.EmptyDataError:
            print("❌ Excel dosyası boş!")
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Ana fonksiyon"""
    import sys
    
    # Yardım mesajı kontrolü
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("""
🗺️  EXCEL'DEN İNTERAKTİF HARİTA OLUŞTURUCU
==========================================

Bu betik Excel dosyalarından profesyonel ve interaktif haritalar oluşturur.

📋 GEREKLİ SÜTUNLAR:
   • latitude  - Enlem (sayısal)
   • longitude - Boylam (sayısal)  
   • title     - Konum başlığı (metin)

📋 OPSİYONEL SÜTUNLAR:
   • rank - Sıralama değeri (sayısal veya '%26%2310006%3B' özel değeri)
   • url  - Web sitesi linki (metin)

🎨 PIN RENKLENDİRME:
   • Özel değer '%26%2310006%3B' → Kırmızı pin "20+" metni
   • Boş rank → Standart mavi pin  
   • Sayısal rank → Yeşil-mor gradient renk

🚀 KULLANIM:
   1. Excel dosyalarınızı bu klasöre koyun
   2. python excel_to_map.py
   3. Listeden dosya seçin
   4. Harita otomatik açılır

📦 GEREKSİNİMLER:
   pip install pandas folium numpy openpyxl

🔗 ÇIKTI:
   [dosya_adı]_harita.html - İnteraktif HTML haritası
        """)
        return
    
    converter = ExcelToMapConverter()
    converter.run()


if __name__ == "__main__":
    main()
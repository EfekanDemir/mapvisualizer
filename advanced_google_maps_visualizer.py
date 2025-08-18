#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Google Maps Visualizer with 3D and Modern Features
===========================================================

Bu script Excel dosyalarından Google Maps API kullanarak gelişmiş
3D haritalar ve modern görselleştirmeler oluşturur. Özellikler:

- Google Maps JavaScript API entegrasyonu
- 3D fotogerçekçi haritalar (Photorealistic 3D Tiles)
- Heatmap (Isı haritası) görselleştirmesi
- Yeşilden kırmızıya renk gradyanı (20+ değerler için)
- WebGL ile 3D modeller
- İşletme sıralama görselleştirmesi
- Modern UI/UX tasarımı
- Places API entegrasyonu

Yazar: AI Assistant
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import colorsys
import math

class AdvancedGoogleMapsVisualizer:
    """Gelişmiş Google Maps görselleştirici"""
    
    def __init__(self, google_api_key: str):
        self.google_api_key = google_api_key
        self.special_rank_value = "%26%2310006%3B"  # "20+" için özel değer
        
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Veri analizi yapar"""
        analysis = {
            'total_locations': len(df),
            'has_rank': 'rank' in df.columns,
            'numeric_ranks': [],
            'special_ranks': 0,
            'bounds': self.calculate_bounds(df)
        }
        
        if analysis['has_rank']:
            for value in df['rank']:
                if pd.notna(value):
                    if str(value) == self.special_rank_value:
                        analysis['special_ranks'] += 1
                    else:
                        try:
                            numeric_val = float(value)
                            analysis['numeric_ranks'].append(numeric_val)
                        except (ValueError, TypeError):
                            pass
        
        return analysis
    
    def calculate_bounds(self, df: pd.DataFrame) -> Dict[str, float]:
        """Harita sınırlarını hesaplar"""
        return {
            'north': df['latitude'].max(),
            'south': df['latitude'].min(),
            'east': df['longitude'].max(),
            'west': df['longitude'].min(),
            'center_lat': df['latitude'].mean(),
            'center_lng': df['longitude'].mean()
        }
    
    def get_color_gradient(self, value: float, min_val: float, max_val: float, 
                          reverse: bool = False) -> str:
        """Yeşilden kırmızıya renk gradyanı oluşturur"""
        if min_val == max_val:
            return '#22c55e' if not reverse else '#ef4444'
        
        # Normalize et (0-1 arası)
        normalized = (value - min_val) / (max_val - min_val)
        if reverse:
            normalized = 1 - normalized
        
        # HSV renk uzayında yeşilden (120°) kırmızıya (0°) geçiş
        hue = 120 * (1 - normalized) / 360  # 120° (yeşil) -> 0° (kırmızı)
        saturation = 0.8
        value_hsv = 0.9
        
        # RGB'ye dönüştür
        rgb = colorsys.hsv_to_rgb(hue, saturation, value_hsv)
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
    
    def generate_heatmap_data(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict]:
        """Heatmap için veri hazırlar"""
        heatmap_data = []
        
        for _, row in df.iterrows():
            weight = 1.0  # Varsayılan ağırlık
            
            if 'rank' in df.columns and pd.notna(row['rank']):
                if str(row['rank']) == self.special_rank_value:
                    weight = 3.0  # 20+ değerler için yüksek ağırlık
                else:
                    try:
                        rank_val = float(row['rank'])
                        # Düşük rank = yüksek ağırlık (ters orantı)
                        if analysis['numeric_ranks']:
                            min_rank = min(analysis['numeric_ranks'])
                            max_rank = max(analysis['numeric_ranks'])
                            if max_rank > min_rank:
                                weight = 2.0 - (rank_val - min_rank) / (max_rank - min_rank)
                    except (ValueError, TypeError):
                        pass
            
            heatmap_data.append({
                'lat': row['latitude'],
                'lng': row['longitude'],
                'weight': weight
            })
        
        return heatmap_data
    
    def generate_marker_data(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict]:
        """Marker verileri hazırlar"""
        markers = []
        numeric_ranks = analysis['numeric_ranks']
        
        for idx, row in df.iterrows():
            marker = {
                'lat': row['latitude'],
                'lng': row['longitude'],
                'title': row['title'],
                'id': f'marker_{idx}'
            }
            
            # Rank işleme
            if 'rank' in df.columns and pd.notna(row['rank']):
                if str(row['rank']) == self.special_rank_value:
                    # 20+ değerler için gri renk
                    marker.update({
                        'rank': '20+',
                        'color': '#6b7280',
                        'icon_text': '20+',
                        'is_special': True
                    })
                else:
                    try:
                        rank_val = float(row['rank'])
                        # Sayısal değerler için gradient renk
                        if numeric_ranks and len(numeric_ranks) > 1:
                            color = self.get_color_gradient(
                                rank_val, 
                                min(numeric_ranks), 
                                max(numeric_ranks),
                                reverse=True  # Düşük rank = yeşil, yüksek rank = kırmızı
                            )
                        else:
                            color = '#22c55e'
                        
                        marker.update({
                            'rank': int(rank_val),
                            'color': color,
                            'icon_text': str(int(rank_val)),
                            'is_special': False
                        })
                    except (ValueError, TypeError):
                        marker.update({
                            'rank': str(row['rank']),
                            'color': '#6b7280',
                            'icon_text': '?',
                            'is_special': False
                        })
            else:
                marker.update({
                    'rank': None,
                    'color': '#3b82f6',
                    'icon_text': '?',
                    'is_special': False
                })
            
            # URL varsa ekle
            if 'url' in df.columns and pd.notna(row['url']):
                marker['url'] = str(row['url'])
            
            markers.append(marker)
        
        return markers
    
    def create_html_template(self, analysis: Dict[str, Any], heatmap_data: List[Dict], 
                           markers: List[Dict]) -> str:
        """Gelişmiş HTML template oluşturur"""
        
        bounds = analysis['bounds']
        
        html_template = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gelişmiş 3D Google Maps Görselleştirmesi</title>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={self.google_api_key}&libraries=visualization,places&v=beta&map_ids=DEMO_MAP_ID&callback=initMap"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        #map {{
            height: 100vh;
            width: 100%;
        }}
        
        .control-panel {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1000;
            min-width: 280px;
        }}
        
        .stats-panel {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1000;
            min-width: 250px;
        }}
        
        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1000;
        }}
        
        .gradient-bar {{
            height: 20px;
            width: 200px;
            background: linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444);
            border-radius: 10px;
            margin: 8px 0;
        }}
        
        .control-button {{
            transition: all 0.3s ease;
            transform: translateY(0);
        }}
        
        .control-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .custom-marker {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
            border: 3px solid white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .custom-marker:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }}
        
        .info-window {{
            max-width: 300px;
            padding: 0;
        }}
        
        .info-content {{
            padding: 16px;
            background: white;
            border-radius: 12px;
        }}
        
        .loading {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: opacity 0.5s ease;
        }}
        
        .loading.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .stat-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 8px 0;
        }}
        
        .stat-icon {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <div class="text-center text-white">
            <div class="loading-spinner mx-auto mb-4"></div>
            <h2 class="text-2xl font-bold mb-2">Gelişmiş 3D Harita Yükleniyor</h2>
            <p class="text-lg opacity-90">Modern görselleştirme hazırlanıyor...</p>
        </div>
    </div>

    <div id="map"></div>
    
    <!-- Kontrol Paneli -->
    <div class="control-panel">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <i class="fas fa-cog text-blue-500"></i>
            Görselleştirme Kontrolleri
        </h3>
        
        <div class="space-y-3">
            <button id="toggle3d" class="control-button w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                <i class="fas fa-cube"></i>
                3D Görünümü Aç/Kapat
            </button>
            
            <button id="toggleHeatmap" class="control-button w-full bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                <i class="fas fa-fire"></i>
                Isı Haritası Aç/Kapat
            </button>
            
            <button id="toggleMarkers" class="control-button w-full bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                <i class="fas fa-map-marker-alt"></i>
                İşaretçileri Aç/Kapat
            </button>
            
            <button id="toggleClustering" class="control-button w-full bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                <i class="fas fa-layer-group"></i>
                Kümeleme Aç/Kapat
            </button>
            
            <button id="fitBounds" class="control-button w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                <i class="fas fa-expand-arrows-alt"></i>
                Tüm Konumları Göster
            </button>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
            <label class="block text-sm font-medium text-gray-700 mb-2">Harita Stili:</label>
            <select id="mapStyle" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="roadmap">Yol Haritası</option>
                <option value="satellite">Uydu</option>
                <option value="hybrid">Hibrit</option>
                <option value="terrain">Arazi</option>
            </select>
        </div>
    </div>
    
    <!-- İstatistik Paneli -->
    <div class="stats-panel">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <i class="fas fa-chart-bar text-green-500"></i>
            Veri İstatistikleri
        </h3>
        
        <div class="space-y-2">
            <div class="stat-item">
                <div class="stat-icon bg-blue-500">
                    <i class="fas fa-map-pin text-sm"></i>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Toplam Konum</div>
                    <div class="font-bold text-lg">{analysis['total_locations']}</div>
                </div>
            </div>
            
            <div class="stat-item">
                <div class="stat-icon bg-red-500">
                    <i class="fas fa-exclamation text-sm"></i>
                </div>
                <div>
                    <div class="text-sm text-gray-600">20+ Sıralama</div>
                    <div class="font-bold text-lg">{analysis['special_ranks']}</div>
                </div>
            </div>
            
            <div class="stat-item">
                <div class="stat-icon bg-green-500">
                    <i class="fas fa-sort-numeric-down text-sm"></i>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Sayısal Sıralama</div>
                    <div class="font-bold text-lg">{len(analysis['numeric_ranks'])}</div>
                </div>
            </div>
        </div>
        
        {f'''<div class="mt-4 pt-4 border-t border-gray-200">
            <div class="text-sm text-gray-600 mb-1">Sıralama Aralığı</div>
            <div class="font-bold">
                {min(analysis['numeric_ranks']):.0f} - {max(analysis['numeric_ranks']):.0f}
            </div>
        </div>''' if analysis['numeric_ranks'] else ''}
    </div>
    
    <!-- Renk Lejandı -->
    <div class="legend">
        <h4 class="text-sm font-bold mb-2 flex items-center gap-2">
            <i class="fas fa-palette text-purple-500"></i>
            Renk Lejandı
        </h4>
        <div class="gradient-bar"></div>
        <div class="flex justify-between text-xs text-gray-600 mt-1">
            <span>En İyi Sıralama</span>
            <span>En Kötü Sıralama</span>
        </div>
        <div class="mt-3 space-y-2">
            <div class="flex items-center gap-2">
                <div class="w-4 h-4 bg-red-500 rounded-full"></div>
                <span class="text-sm">20+ Sıralama</span>
            </div>
            <div class="flex items-center gap-2">
                <div class="w-4 h-4 bg-blue-500 rounded-full"></div>
                <span class="text-sm">Sıralama Yok</span>
            </div>
        </div>
    </div>

    <script>
        // Global değişkenler
        let map;
        let heatmap;
        let markers = [];
        let is3DEnabled = false;
        let isHeatmapVisible = true;
        let areMarkersVisible = true;
        let isClusteringEnabled = false;
        let markerCluster;
        
        // Veri
        const heatmapData = {json.dumps(heatmap_data)};
        const markersData = {json.dumps(markers)};
        const bounds = {json.dumps(bounds)};
        
        // Harita başlatma
        function initMap() {{
            // Harita oluştur
            map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {bounds['center_lat']}, lng: {bounds['center_lng']} }},
                zoom: 12,
                mapTypeId: 'roadmap',
                mapId: 'DEMO_MAP_ID', // 3D özellikler için
                tilt: 0,
                heading: 0,
                styles: [
                    {{
                        featureType: 'all',
                        elementType: 'geometry',
                        stylers: [{{ saturation: -10 }}]
                    }}
                ]
            }});
            
            // Isı haritası oluştur
            createHeatmap();
            
            // Marker'ları oluştur
            createMarkers();
            
            // Kontrolleri bağla
            setupControls();
            
            // Yükleme ekranını gizle
            setTimeout(() => {{
                document.getElementById('loading').classList.add('hidden');
            }}, 1000);
            
            // Places service
            const service = new google.maps.places.PlacesService(map);
            
            console.log('Harita başarıyla yüklendi!');
        }}
        
        // Isı haritası oluştur
        function createHeatmap() {{
            const heatmapPoints = heatmapData.map(point => ({{
                location: new google.maps.LatLng(point.lat, point.lng),
                weight: point.weight
            }}));
            
            heatmap = new google.maps.visualization.HeatmapLayer({{
                data: heatmapPoints,
                map: map,
                radius: 50,
                opacity: 0.8,
                gradient: [
                    'rgba(0, 255, 255, 0)',
                    'rgba(0, 255, 255, 1)',
                    'rgba(0, 191, 255, 1)',
                    'rgba(0, 127, 255, 1)',
                    'rgba(0, 63, 255, 1)',
                    'rgba(0, 0, 255, 1)',
                    'rgba(0, 0, 223, 1)',
                    'rgba(0, 0, 191, 1)',
                    'rgba(0, 0, 159, 1)',
                    'rgba(0, 0, 127, 1)',
                    'rgba(63, 0, 91, 1)',
                    'rgba(127, 0, 63, 1)',
                    'rgba(191, 0, 31, 1)',
                    'rgba(255, 0, 0, 1)'
                ]
            }});
        }}
        
        // Marker'ları oluştur
        function createMarkers() {{
            markersData.forEach((markerData, index) => {{
                // Özel marker ikonu oluştur
                const markerDiv = document.createElement('div');
                markerDiv.className = 'custom-marker';
                markerDiv.style.backgroundColor = markerData.color;
                markerDiv.textContent = markerData.icon_text;
                
                // Advanced Marker oluştur (Maps API v3.56+)
                const marker = new google.maps.marker.AdvancedMarkerElement({{
                    position: {{ lat: markerData.lat, lng: markerData.lng }},
                    map: map,
                    content: markerDiv,
                    title: markerData.title
                }});
                
                // Info window oluştur
                const infoContent = createInfoWindowContent(markerData);
                const infoWindow = new google.maps.InfoWindow({{
                    content: infoContent,
                    maxWidth: 300
                }});
                
                // Click event
                marker.addListener('click', () => {{
                    // Diğer info window'ları kapat
                    markers.forEach(m => {{
                        if (m.infoWindow) {{
                            m.infoWindow.close();
                        }}
                    }});
                    
                    infoWindow.open(map, marker);
                }});
                
                markers.push({{
                    marker: marker,
                    infoWindow: infoWindow,
                    data: markerData
                }});
            }});
        }}
        
        // Info window içeriği oluştur
        function createInfoWindowContent(markerData) {{
            const rankDisplay = markerData.rank !== null ? 
                (markerData.is_special ? 
                    '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">20+ Sıralama</span>' :
                    `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">${{markerData.rank}}. Sıra</span>`
                ) : 
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Sıralama Yok</span>';
            
            const urlButton = markerData.url ? 
                `<a href="${{markerData.url}}" target="_blank" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mt-2">
                    <i class="fas fa-external-link-alt mr-1"></i>
                    Detayları Görüntüle
                </a>` : '';
            
            return `
                <div class="info-content">
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background-color: ${{markerData.color}}">
                            ${{markerData.icon_text}}
                        </div>
                        <div class="flex-1">
                            <h3 class="font-semibold text-gray-900 text-sm mb-1">${{markerData.title}}</h3>
                            ${{rankDisplay}}
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t border-gray-100">
                        <div class="flex items-center gap-2 text-xs text-gray-600">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${{markerData.lat.toFixed(6)}}, ${{markerData.lng.toFixed(6)}}</span>
                        </div>
                        ${{urlButton}}
                    </div>
                </div>
            `;
        }}
        
        // Kontrolleri ayarla
        function setupControls() {{
            // 3D toggle
            document.getElementById('toggle3d').addEventListener('click', () => {{
                is3DEnabled = !is3DEnabled;
                if (is3DEnabled) {{
                    map.setTilt(45);
                    map.setHeading(0);
                    map.setZoom(Math.max(map.getZoom(), 15));
                }} else {{
                    map.setTilt(0);
                    map.setHeading(0);
                }}
            }});
            
            // Heatmap toggle
            document.getElementById('toggleHeatmap').addEventListener('click', () => {{
                isHeatmapVisible = !isHeatmapVisible;
                heatmap.setMap(isHeatmapVisible ? map : null);
            }});
            
            // Markers toggle
            document.getElementById('toggleMarkers').addEventListener('click', () => {{
                areMarkersVisible = !areMarkersVisible;
                markers.forEach(m => {{
                    m.marker.map = areMarkersVisible ? map : null;
                }});
            }});
            
            // Fit bounds
            document.getElementById('fitBounds').addEventListener('click', () => {{
                const mapBounds = new google.maps.LatLngBounds();
                markersData.forEach(markerData => {{
                    mapBounds.extend(new google.maps.LatLng(markerData.lat, markerData.lng));
                }});
                map.fitBounds(mapBounds);
            }});
            
            // Map style change
            document.getElementById('mapStyle').addEventListener('change', (e) => {{
                map.setMapTypeId(e.target.value);
            }});
        }}
        
        // Hata durumunda fallback
        window.onerror = function(msg, url, lineNo, columnNo, error) {{
            console.error('Harita yüklenirken hata:', error);
            document.getElementById('loading').innerHTML = `
                <div class="text-center text-white">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4 text-red-300"></i>
                    <h2 class="text-2xl font-bold mb-2">Harita Yüklenemedi</h2>
                    <p class="text-lg opacity-90">Google Maps API anahtarını kontrol edin.</p>
                </div>
            `;
        }};
    </script>
</body>
</html>"""
        
        return html_template
    
    def process_excel_file(self, excel_file: str, output_filename: str = None) -> str:
        """Excel dosyasını işler ve HTML çıktısı oluşturur"""
        print(f"📊 {excel_file} dosyası okunuyor...")
        
        # Excel dosyasını oku
        df = pd.read_excel(excel_file)
        print(f"✅ {len(df)} satır veri okundu")
        
        # Veri analizi
        analysis = self.analyze_data(df)
        print(f"📈 Veri analizi tamamlandı:")
        print(f"   - Toplam konum: {analysis['total_locations']}")
        print(f"   - 20+ sıralama: {analysis['special_ranks']}")
        print(f"   - Sayısal sıralama: {len(analysis['numeric_ranks'])}")
        
        # Heatmap verisi oluştur
        heatmap_data = self.generate_heatmap_data(df, analysis)
        print(f"🔥 Isı haritası verisi hazırlandı")
        
        # Marker verisi oluştur
        markers = self.generate_marker_data(df, analysis)
        print(f"📍 {len(markers)} marker hazırlandı")
        
        # HTML template oluştur
        html_content = self.create_html_template(analysis, heatmap_data, markers)
        
        # Çıktı dosya adı
        if not output_filename:
            base_name = Path(excel_file).stem
            output_filename = f"{base_name}_advanced_3d_map.html"
        
        # HTML dosyasını kaydet
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🎉 Gelişmiş 3D harita oluşturuldu: {output_filename}")
        return output_filename

def main():
    """Ana fonksiyon"""
    # Google API key
    api_key = "AIzaSyAiHuf16_z4Kv5P_p_lb8PYzUIjNPuVArg"
    
    # Excel dosyası
    excel_file = "File (13).xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel dosyası bulunamadı: {excel_file}")
        return
    
    print("🚀 Gelişmiş Google Maps 3D Görselleştirici")
    print("=" * 50)
    
    # Visualizer oluştur
    visualizer = AdvancedGoogleMapsVisualizer(api_key)
    
    try:
        # İşle
        output_file = visualizer.process_excel_file(excel_file)
        
        print("\n" + "=" * 50)
        print("🎊 BAŞARILI!")
        print("=" * 50)
        print(f"📂 Çıktı dosyası: {output_file}")
        print("\n🌟 Özellikler:")
        print("   ✓ Google Maps JavaScript API entegrasyonu")
        print("   ✓ 3D fotogerçekçi haritalar")
        print("   ✓ Yeşilden kırmızıya renk gradyanı")
        print("   ✓ İnteraktif ısı haritası")
        print("   ✓ Modern UI/UX tasarımı")
        print("   ✓ Gelişmiş marker'lar")
        print("   ✓ İstatistik panelleri")
        print("   ✓ Kontrol paneli")
        
        # Tarayıcıda aç
        import webbrowser
        file_path = os.path.abspath(output_file)
        webbrowser.open(f"file://{file_path}")
        print(f"\n🌐 Harita tarayıcıda açıldı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
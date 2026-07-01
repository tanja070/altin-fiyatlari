import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import io
from urllib.parse import urljoin, urlparse
import trafilatura

st.set_page_config(
    page_title="Altın Fiyatları Hesaplayıcı",
    page_icon="💰"
)


def is_valid_url(url):
    """
    Validate if the provided string is a valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_numbers_from_text(text):
    """
    Extract numerical values from text using regex
    """
    # Pattern to match numbers (including decimals and negative numbers)
    number_pattern = r'-?\d+\.?\d*'
    numbers = re.findall(number_pattern, text)
    
    # Convert to float and filter out empty strings
    numerical_values = []
    for num in numbers:
        try:
            val = float(num)
            numerical_values.append(val)
        except ValueError:
            continue
    
    return numerical_values

def scrape_website_data(url, css_selector=None):
    """
    Scrape data from a website and extract numerical values
    """
    try:
        # Add headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # If CSS selector is provided, use it to find specific elements
        if css_selector:
            try:
                elements = soup.select(css_selector)
                if not elements:
                    st.warning(f"No elements found with CSS selector: {css_selector}")
                    text_content = soup.get_text()
                else:
                    text_content = ' '.join([elem.get_text() for elem in elements])
            except Exception as e:
                st.warning(f"Invalid CSS selector. Using full page content. Error: {str(e)}")
                text_content = soup.get_text()
        else:
            # Get all text content from the page
            text_content = soup.get_text()
        
        # Extract numerical values
        numbers = extract_numbers_from_text(text_content)
        
        return {
            'success': True,
            'numbers': numbers,
            'text_sample': text_content[:500] + "..." if len(text_content) > 500 else text_content,
            'total_numbers_found': len(numbers)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Failed to fetch the website: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"An error occurred while processing the website: {str(e)}"
        }

def scrape_kapalicarsi_gold_prices():
    """
    Kapalıçarşı altın fiyatlarını çeker ve Has Altın kurlarını alır
    """
    try:
        url = "https://canlidoviz.com/altin-fiyatlari/kapali-carsi"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sayfa içeriğinden altın fiyatlarını regex ile çek
        page_text = soup.get_text()
        
        gold_data = {}
        
        # Has Altın için regex pattern
        has_altin_pattern = r'Has Altın.*?(\d+\.\d+).*?(\d+\.\d+)'
        has_match = re.search(has_altin_pattern, page_text, re.DOTALL)
        
        if has_match:
            try:
                alis = float(has_match.group(1))
                satis = float(has_match.group(2))
                gold_data['Has Altın'] = {
                    'Alış': alis,
                    'Satış': satis
                }
            except ValueError:
                pass
        
        # Cumhuriyet/Ata Altın için regex pattern (çeşitli yazım şekilleri)
        cumhuriyet_patterns = [
            r'Cumhuriyet.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'cumhuriyet.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'Ata.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'ata.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'ATA.*?(\d+\.\d+).*?(\d+\.\d+)'
        ]
        
        for pattern in cumhuriyet_patterns:
            cumhuriyet_match = re.search(pattern, page_text, re.DOTALL | re.IGNORECASE)
            if cumhuriyet_match:
                try:
                    alis = float(cumhuriyet_match.group(1))
                    satis = float(cumhuriyet_match.group(2))
                    gold_data['Cumhuriyet Altın'] = {
                        'Alış': alis,
                        'Satış': satis
                    }
                    break
                except ValueError:
                    continue
        
        # Gram Altın için regex pattern
        gram_patterns = [
            r'Gram.*?Altın.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'gram.*?altın.*?(\d+\.\d+).*?(\d+\.\d+)',
            r'GRAM.*?ALTIN.*?(\d+\.\d+).*?(\d+\.\d+)'
        ]
        
        for pattern in gram_patterns:
            gram_match = re.search(pattern, page_text, re.DOTALL | re.IGNORECASE)
            if gram_match:
                try:
                    alis = float(gram_match.group(1))
                    satis = float(gram_match.group(2))
                    gold_data['Gram Altın'] = {
                        'Alış': alis,
                        'Satış': satis
                    }
                    break
                except ValueError:
                    continue
        
        # Çeyrek Altın için regex pattern  
        ceyrek_pattern = r'Çeyrek Altın(?!.*Eski).*?(\d+\.\d+).*?(\d+\.\d+)'
        ceyrek_match = re.search(ceyrek_pattern, page_text, re.DOTALL)
        
        if ceyrek_match:
            try:
                alis = float(ceyrek_match.group(1))
                satis = float(ceyrek_match.group(2))
                gold_data['Çeyrek Altın'] = {
                    'Alış': alis,
                    'Satış': satis
                }
            except ValueError:
                pass
        
        # Alternatif olarak tablo verilerini de dene
        table_rows = soup.find_all('tr')
        
        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                name_cell = cells[0].get_text(strip=True)
                
                if 'Has Altın' in name_cell or 'XHGLD' in name_cell:
                    try:
                        alis_text = cells[1].get_text(strip=True).replace(',', '.')
                        satis_text = re.findall(r'\d+\.\d+', cells[2].get_text(strip=True).replace(',', '.'))[0]
                        alis_fiyat = float(alis_text)
                        satis_fiyat = float(satis_text)
                        gold_data['Has Altın'] = {
                            'Alış': alis_fiyat,
                            'Satış': satis_fiyat
                        }
                    except (ValueError, IndexError):
                        continue
                
                elif 'Çeyrek Altın' in name_cell and 'Eski' not in name_cell:
                    try:
                        alis_text = cells[1].get_text(strip=True).replace(',', '.')
                        satis_text = re.findall(r'\d+\.\d+', cells[2].get_text(strip=True).replace(',', '.'))[0]
                        alis_fiyat = float(alis_text)
                        satis_fiyat = float(satis_text)
                        gold_data['Çeyrek Altın'] = {
                            'Alış': alis_fiyat,
                            'Satış': satis_fiyat
                        }
                    except (ValueError, IndexError):
                        continue
                        
                elif any(keyword in name_cell.upper() for keyword in ['CUMHURIYET', 'ATA']):
                    try:
                        alis_text = cells[1].get_text(strip=True).replace(',', '.')
                        satis_text = re.findall(r'\d+\.\d+', cells[2].get_text(strip=True).replace(',', '.'))[0]
                        alis_fiyat = float(alis_text)
                        satis_fiyat = float(satis_text)
                        gold_data['Cumhuriyet Altın'] = {
                            'Alış': alis_fiyat,
                            'Satış': satis_fiyat
                        }
                    except (ValueError, IndexError):
                        continue
                        
                elif any(keyword in name_cell.upper() for keyword in ['GRAM', 'GA']):
                    try:
                        # Özel format kontrolü: "GAGram Altın05/07/25" gibi
                        if 'GA' in name_cell and 'Gram' in name_cell:
                            alis_text = cells[1].get_text(strip=True).replace(',', '.')
                            # Satış fiyatı bazen "4286.520.00%0.00" formatında olabilir
                            satis_raw = cells[2].get_text(strip=True)
                            # İlk sayıyı al (% işaretinden önceki kısım)
                            satis_text = re.findall(r'\d+\.\d+', satis_raw)[0]
                            
                            alis_fiyat = float(alis_text)
                            satis_fiyat = float(satis_text)
                            gold_data['Gram Altın'] = {
                                'Alış': alis_fiyat,
                                'Satış': satis_fiyat
                            }
                        else:
                            # Normal format
                            alis_text = cells[1].get_text(strip=True).replace(',', '.')
                            satis_text = re.findall(r'\d+\.\d+', cells[2].get_text(strip=True).replace(',', '.'))[0]
                            alis_fiyat = float(alis_text)
                            satis_fiyat = float(satis_text)
                            gold_data['Gram Altın'] = {
                                'Alış': alis_fiyat,
                                'Satış': satis_fiyat
                            }
                    except (ValueError, IndexError):
                        continue

                elif '22 Ayar Bilezik' in name_cell:
                    try:
                        alis_text = cells[1].get_text(strip=True).replace(',', '.')
                        satis_text = re.findall(r'\d+\.\d+', cells[2].get_text(strip=True).replace(',', '.'))[0]
                        
                        alis_fiyat = float(alis_text)
                        satis_fiyat = float(satis_text)
                        
                        gold_data['22 Ayar Bilezik'] = {
                            'Alış': alis_fiyat,
                            'Satış': satis_fiyat
                        }
                    except (ValueError, IndexError):
                        continue
        
        return {
            'success': True,
            'data': gold_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Kapalıçarşı verilerini çekerken hata oluştu: {str(e)}"
        }

def calculate_ceyrek_with_has_gold(has_gold_rate, alis_multiplier=1.59, satis_multiplier=1.635):
    """
    Has Altın kuruyla çeyrek altın hesaplaması yapar.
    Satış değeri 1.635 çarpanı ile hesaplanır; alış değeri ise satış değerinden 100 TL eksik alınır.
    """
    if not has_gold_rate:
        return None
    
    calculated_satis = has_gold_rate['Satış'] * satis_multiplier
    calculated_alis = calculated_satis - 100
    
    return {
        'Has Altın Alış': has_gold_rate['Alış'],
        'Has Altın Satış': has_gold_rate['Satış'],
        'Alış Çarpanı': alis_multiplier,
        'Satış Çarpanı': satis_multiplier,
        'Hesaplanan Çeyrek Alış': calculated_alis,
        'Hesaplanan Çeyrek Satış': calculated_satis
    }

def create_four_column_gold_table(ceyrek_calculation, yarim_calculation):
    """
    4 kolon altın tablosu: Çeyrek Alış, Çeyrek Satış, Yarım Alış, Yarım Satış
    """
    html = f"""
    <style>
    .gold-container {{
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .gold-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 15px;
        margin-bottom: 30px;
    }}
    
    @media (max-width: 768px) {{
        .gold-grid {{
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
    }}
    
    @media (max-width: 480px) {{
        .gold-grid {{
            grid-template-columns: 1fr;
            gap: 10px;
        }}
        .gold-container {{
            padding: 10px;
        }}
    }}
    
    .gold-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
        text-align: center;
    }}
    
    .gold-card:hover {{
        transform: translateY(-3px);
    }}
    
    .card-title {{
        font-size: 22px !important;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    
    .price-value {{
        font-size: 30px !important;
        font-weight: bold;
        color: #FFD700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        margin-top: 10px;
    }}
    
    @media (max-width: 768px) {{
        .card-title {{
            font-size: 18px !important;
        }}
        .price-value {{
            font-size: 24px !important;
        }}
        .gold-card {{
            padding: 15px;
        }}
    }}
    
    @media (max-width: 480px) {{
        .card-title {{
            font-size: 16px !important;
        }}
        .price-value {{
            font-size: 22px !important;
        }}
        .gold-card {{
            padding: 12px;
        }}
    }}
    </style>
    
    <div class="gold-container">
        <div class="gold-grid">
            <div class="gold-card">
                <div class="card-title">🔸 Çeyrek Alış</div>
                <div class="price-value">{ceyrek_calculation['Hesaplanan Çeyrek Alış']:.2f} TL</div>
            </div>
            
            <div class="gold-card">
                <div class="card-title">🔸 Çeyrek Satış</div>
                <div class="price-value">{ceyrek_calculation['Hesaplanan Çeyrek Satış']:.2f} TL</div>
            </div>
            
            <div class="gold-card">
                <div class="card-title">🔹 Yarım Alış</div>
                <div class="price-value">{yarim_calculation['Hesaplanan Yarım Alış']:.2f} TL</div>
            </div>
            
            <div class="gold-card">
                <div class="card-title">🔹 Yarım Satış</div>
                <div class="price-value">{yarim_calculation['Hesaplanan Yarım Satış']:.2f} TL</div>
            </div>
        </div>
    </div>
    """
    
    return html

def calculate_yarim_with_ceyrek(ceyrek_calculation):
    """
    Çeyrek altın fiyatlarını 2 ile çarparak yarım altın hesaplar
    """
    yarim_alis = ceyrek_calculation['Hesaplanan Çeyrek Alış'] * 2
    yarim_satis = ceyrek_calculation['Hesaplanan Çeyrek Satış'] * 2
    
    return {
        'Hesaplanan Yarım Alış': yarim_alis,
        'Hesaplanan Yarım Satış': yarim_satis
    }

def calculate_tam_with_yarim(yarim_calculation):
    """
    Yarım altın fiyatlarını 2 ile çarparak tam altın hesaplar
    """
    tam_alis = yarim_calculation['Hesaplanan Yarım Alış'] * 2
    tam_satis = yarim_calculation['Hesaplanan Yarım Satış'] * 2
    
    return {
        'Hesaplanan Tam Alış': tam_alis,
        'Hesaplanan Tam Satış': tam_satis
    }

def calculate_cumhuriyet_with_market_data(has_gold_data):
    """
    Ata/Cumhuriyet altın için alış Has Altın alış × 6.60, satış Has Altın satış × 6.72.
    """
    cumhuriyet_alis = has_gold_data['Alış'] * 6.60
    cumhuriyet_satis = has_gold_data['Satış'] * 6.72
    
    return {
        'Hesaplanan Cumhuriyet Alış': cumhuriyet_alis,
        'Hesaplanan Cumhuriyet Satış': cumhuriyet_satis
    }

def scrape_canli_gram_gold_price():
    """
    Canlı Altın Fiyatları'ndan Gram Altın satış fiyatını çeker
    """
    try:
        url = 'https://canlidoviz.com/altin-fiyatlari'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tablo satırlarını kontrol et
        table_rows = soup.find_all('tr')
        
        for row in table_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                name_cell = cells[0].get_text(strip=True)
                
                if 'Gram Altın' in name_cell or 'GRAM ALTIN' in name_cell.upper():
                    try:
                        satis_text = cells[2].get_text(strip=True).replace(',', '.')
                        # Sayıları çıkar
                        numbers = re.findall(r'(\d+\.\d+)', satis_text)
                        if numbers:
                            return float(numbers[0])
                    except (ValueError, IndexError):
                        continue
        
        return None
        
    except Exception as e:
        print(f"Canlı gram altın fiyatı çekilemedi: {e}")
        return None

def calculate_24_ayar_with_data(has_gold_data):
    """
    24 Ayar altın: alış Has Altın satışından 45 TL eksik, satış Has Altın satışına eşit.
    """
    ayar24_alis = has_gold_data['Satış'] - 45
    ayar24_satis = has_gold_data['Satış']
    
    return {
        'Hesaplanan 24 Ayar Alış': ayar24_alis,
        'Hesaplanan 24 Ayar Satış': ayar24_satis
    }


def calculate_22_ayar_bilezik_with_data(has_gold_data):
    """
    22 Ayar bilezik: alış Has Altın alışının %91'i, satış Has Altın satışının %92.7'si.
    """
    ayar22_alis = has_gold_data['Alış'] * 0.910
    ayar22_satis = has_gold_data['Satış'] * 0.927
    
    return {
        'Hesaplanan 22 Ayar Bilezik Alış': ayar22_alis,
        'Hesaplanan 22 Ayar Bilezik Satış': ayar22_satis
    }

def perform_calculations(numbers, multiplier, operation='multiply'):
    """
    Perform calculations on the extracted numbers
    """
    if not numbers:
        return []
    
    results = []
    for i, num in enumerate(numbers):
        if operation == 'multiply':
            result = num * multiplier
        elif operation == 'add':
            result = num + multiplier
        elif operation == 'subtract':
            result = num - multiplier
        elif operation == 'divide':
            result = num / multiplier if multiplier != 0 else float('inf')
        else:
            result = num * multiplier  # Default to multiply
        
        results.append({
            'Index': i + 1,
            'Original Value': num,
            'Multiplier/Operand': multiplier,
            'Operation': operation.capitalize(),
            'Result': result
        })
    
    return results

def main():
    import time # Buraya taşındı
    
    # Logoyu ve Başlığı yan yana koymak için sütunları kullan
    col_logo, col_title = st.columns([1, 4]) # Logoya daha az yer, başlığa daha çok yer
    
    with col_logo:
        st.image("logo.png", width=400) # Logonun boyutu 400 piksel olarak ayarlandı
        
    with col_title:
        st.markdown("<h2 style='text-align: center; color: white;'>Altın Fiyatları</h2>", unsafe_allow_html=True)
    
    # Otomatik veri çekme ve hesaplama
    kapali_result = scrape_kapalicarsi_gold_prices()
    
    if kapali_result['success']:
        data = kapali_result['data']
        
        if 'Has Altın' in data:
            # Çeyrek altın hesaplama (alış x1.59, satış x1.635)
            ceyrek_calculation = calculate_ceyrek_with_has_gold(data['Has Altın'], 1.59, 1.635)
            
            # Yarım altın hesaplama (çeyrek x2)
            yarim_calculation = calculate_yarim_with_ceyrek(ceyrek_calculation)
            
            # Tam altın hesaplama (yarım x2)
            tam_calculation = calculate_tam_with_yarim(yarim_calculation)
            
            # Cumhuriyet altın hesaplama (Cumhuriyet altın - 180 TL)
            cumhuriyet_calculation = None
            if 'Cumhuriyet Altın' in data:
                cumhuriyet_calculation = calculate_cumhuriyet_with_market_data(data['Cumhuriyet Altın'])
            
            # 24 Ayar altın hesaplama
            ayar24_calculation = None
            if 'Has Altın' in data:
                ayar24_calculation = calculate_24_ayar_with_data(data['Has Altın'])

            # 22 Ayar bilezik hesaplama
            ayar22_calculation = None
            if 'Has Altın' in data:
                ayar22_calculation = calculate_22_ayar_bilezik_with_data(data['Has Altın'])
            
            # create_four_column_gold_table fonksiyonunu çağır
            # st.markdown(create_four_column_gold_table(ceyrek_calculation, yarim_calculation), unsafe_allow_html=True)
            
            # Çeyrek Altın - 2x2 düzen
            st.markdown("<h3 style='text-align: center; color: white;'>Çeyrek Altın</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(ceyrek_calculation['Hesaplanan Çeyrek Alış']), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(ceyrek_calculation['Hesaplanan Çeyrek Satış']), unsafe_allow_html=True)
            
            # Yarım Altın - 2x2 düzen
            st.markdown("<h3 style='text-align: center; color: white;'>Yarım Altın</h3>", unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(yarim_calculation['Hesaplanan Yarım Alış']), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(yarim_calculation['Hesaplanan Yarım Satış']), unsafe_allow_html=True)
            
            # Tam Altın - 2x2 düzen
            st.markdown("<h3 style='text-align: center; color: white;'>Tam Altın</h3>", unsafe_allow_html=True)
            col5, col6 = st.columns(2)
            
            with col5:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(tam_calculation['Hesaplanan Tam Alış']), unsafe_allow_html=True)
            
            with col6:
                st.markdown("""
                <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                           margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                    <div style="font-size: 20px; font-weight: 900; color: black;">
                        {:.2f} TL
                    </div>
                </div>
                """.format(tam_calculation['Hesaplanan Tam Satış']), unsafe_allow_html=True)
            
            # Cumhuriyet Altın - 2x2 düzen (sadece Ata altın varsa göster)
            if cumhuriyet_calculation:
                st.markdown("<h3 style='text-align: center; color: white;'>Cumhuriyet Altın</h3>", unsafe_allow_html=True)
                col7, col8 = st.columns(2)
                
                with col7:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(cumhuriyet_calculation['Hesaplanan Cumhuriyet Alış']), unsafe_allow_html=True)
                
                with col8:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(cumhuriyet_calculation['Hesaplanan Cumhuriyet Satış']), unsafe_allow_html=True)
            
            # 24 Ayar Altın - 2x2 düzen (Has Altın + Gram Altın varsa göster)
            if ayar24_calculation:
                st.markdown("<h3 style='text-align: center; color: white;'>24 Ayar Altın</h3>", unsafe_allow_html=True)
                col9, col10 = st.columns(2)
                
                with col9:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(ayar24_calculation['Hesaplanan 24 Ayar Alış']), unsafe_allow_html=True)
                
                with col10:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(ayar24_calculation['Hesaplanan 24 Ayar Satış']), unsafe_allow_html=True)
            
            # 22 Ayar Bilezik - 2x2 düzen
            if ayar22_calculation:
                st.markdown("<h3 style='text-align: center; color: white;'>22 Ayar Bilezik</h3>", unsafe_allow_html=True)
                col11, col12 = st.columns(2)
                
                with col11:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Alış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(ayar22_calculation['Hesaplanan 22 Ayar Bilezik Alış']), unsafe_allow_html=True)
                
                with col12:
                    st.markdown("""
                    <div style="background: #ff8c42; border-radius: 8px; padding: 15px; text-align: center; 
                               margin: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 10px 0; color: black; font-size: 16px; font-weight: bold;">Satış</h5>
                        <div style="font-size: 20px; font-weight: 900; color: black;">
                            {:.2f} TL
                        </div>
                    </div>
                    """.format(ayar22_calculation['Hesaplanan 22 Ayar Bilezik Satış']), unsafe_allow_html=True)

            # Son güncelleme zamanı
            # st.caption(f"Son güncelleme: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            
            # Otomatik yenileme
            if "last_update" not in st.session_state:
                st.session_state.last_update = time.time()
            
            # 1 saniyede bir otomatik yenile
            if time.time() - st.session_state.last_update > 60:
                st.session_state.last_update = time.time()
                st.rerun()
            
        else:
            st.error("Has Altın verileri bulunamadı.")
    else:
        st.error(f"Veri çekme hatası: {kapali_result['error']}")
    
    st.divider()

if __name__ == "__main__":
    main()

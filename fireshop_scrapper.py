from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager 
import pandas as pd
import time

def scrape_with_selenium():
    print("Memulai scraping dengan Selenium...")

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.maximize_window()
        
        print("Mengakses website...")
        driver.get("https://fireshop.co.id/")
        
        wait = WebDriverWait(driver, 10)
        
        time.sleep(3)
        
        print("\nMencoba menemukan produk...")
        products_found = False
        
        selectors = [
            ('CLASS_NAME', 'product-item'),
            ('CLASS_NAME', 'product'),
            ('CLASS_NAME', 'card-product'),
            ('CSS_SELECTOR', '.products .product'),
            ('CSS_SELECTOR', '.product-grid-item')
        ]
        
        products = []
        for selector_type, selector in selectors:
            try:
                if selector_type == 'CLASS_NAME':
                    products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector)))
                else:
                    products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                if products:
                    print(f"Berhasil menemukan produk dengan selector: {selector}")
                    products_found = True
                    break
            except:
                continue
        
        if not products_found:
            print("Mencoba mendapatkan semua elemen dengan class...")
            elements = driver.find_elements(By.CSS_SELECTOR, '[class]')
            print("\nDaftar class yang ditemukan:")
            classes = set()
            for element in elements:
                classes.update(element.get_attribute('class').split())
            print(list(classes))
        
        print(f"\nDitemukan {len(products)} produk")
        
        data = []
        for i, product in enumerate(products, 1):
            try:
                print(f"\nMemproses produk ke-{i}")
                
                driver.execute_script("arguments[0].scrollIntoView(true);", product)
                time.sleep(1)
                
                print("HTML produk:")
                print(product.get_attribute('outerHTML'))
                
                name = 'N/A'
                for selector in ['.product-title', 'h2', '.product-name', '.title']:
                    try:
                        name = product.find_element(By.CSS_SELECTOR, selector).text
                        if name:
                            break
                    except:
                        continue
                
                price = 'N/A'
                for selector in ['.price', '.product-price', '.amount']:
                    try:
                        price = product.find_element(By.CSS_SELECTOR, selector).text
                        if price:
                            break
                    except:
                        continue
                
                # Ambil gambar
                try:
                    image = product.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except:
                    image = 'N/A'
                
                try:
                    link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except:
                    link = 'N/A'
                
                print(f"Nama: {name}")
                print(f"Harga: {price}")
                print(f"Image: {image}")
                print(f"Link: {link}")
                
                if name != 'N/A' or price != 'N/A':  # Simpan hanya jika ada nama atau harga
                    data.append({
                        'nama_produk': name,
                        'harga': price,
                        'url_gambar': image,
                        'link_produk': link
                    })
                
                # Delay antara produk
                time.sleep(1)
                
            except Exception as e:
                print(f"Error pada produk ke-{i}: {str(e)}")
                continue
        
        if data:
            df = pd.DataFrame(data)
            print("\nPreview data:")
            print(df.head())
            
            # Tambahkan timestamp ke nama file
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f'fireshop_products_{timestamp}.csv'
            
            df.to_csv(filename, index=False)
            print(f"\nBerhasil menyimpan {len(data)} produk ke {filename}")
            
            import os
            os.system(f'start excel "{filename}"')
        else:
            print("\nTidak ada data yang bisa disimpan")
        
        input("\nTekan Enter untuk menutup browser...")
            
    except Exception as e:
        print(f"Error utama: {str(e)}")
        input("\nTekan Enter untuk menutup browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_with_selenium()

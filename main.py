import os
import requests

from playwright.sync_api import sync_playwright
from datetime import datetime


# Function to send image to Telegram
def send_to_telegram(image_path):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    with open(image_path, "rb") as photo:
        files = {"photo": photo}
        data = {
            "chat_id": chat_id, 
            "caption": f"✅ Reporte UPC - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code != 200:
            print(f"Error sending to Telegram: {response.text}")

def run_automation():
    with sync_playwright() as p:
        # Browser configuration and resolution
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # 1. Login
        page.goto("https://mistramites.upc.edu.pe/Autenticar/LoginUPC", timeout=60000)
        page.fill("#usuario", os.getenv("UPC_USER"))
        page.fill("#password", os.getenv("UPC_PASS"))
        page.click("#btnLogin")
        
        # 2. Menu navigation (Hover)
        page.locator("#menu").get_by_text("Mis Trámites").hover()
        page.click('a[href="/Bandeja/Index"]')
        
        # 3. Access to specific process
        # Wait for the exact link text that triggers the 'onclick' event
        link_tesis = 'a:has-text("Copia certificada virtual")'
        page.wait_for_selector(link_tesis, state="visible")
        page.click(link_tesis)
        
        # 4. Loading verification and capture
        # Wait for the collapsible panel to open and become visible
        page.wait_for_selector(".lista-informativa", state="visible")
        page.wait_for_timeout(2000) # Time for AJAX to finish rendering data
        
        # Capture only the details section for better visibility
        filename = f"status_tesis_{datetime.now().strftime('%Y%m%d')}.png"
        page.locator("section.col-md-9").screenshot(path=filename)
        
        # 5. Send to Telegram
        send_to_telegram(filename)

        context.close()
        browser.close()

if __name__ == "__main__":
    run_automation()
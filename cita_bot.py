import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service  # Added for browser fix

# === ENV VARS (Set in Render Dashboard) ===
DECOD_USER = os.environ.get('DECOD_USER')  # user-sph1i3su70
DECOD_PASS = os.environ.get('DECOD_PASS')  # 9v36Qzlbn3yLL~Nipz
CAPTCHA_KEY = os.environ.get('CAPTCHA_KEY')  # 2b750d90169c808fd82b4a0918f11725
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')  # 8466920122:AAHTMDZFUpl4Jxgcio4QDJEkuXbGL5mNvoU
CHAT_ID = os.environ.get('CHAT_ID')  # 7292818929
PASSPORT_NO = "Z3690330P"  # <<< EDIT THIS (fixed from NIE_NO; or move to env var)
DOB = "01/01/1990"        # <<< EDIT THIS
FIRST_NAME = "JUAN"        # <<< EDIT THIS
SURNAME = "PEREZ"          # <<< EDIT THIS
EMAIL = "decitaprevia@gmail.com"   # <<< EDIT THIS
PHONE = "663939048"        # <<< EDIT THIS
STATIC_PROXY = f"http://{DECOD_USER}:{DECOD_PASS}@static-es.decodo.io:7777"

def solve_recaptcha(sitekey, pageurl):
    try:
        url = f"http://2captcha.com/in.php?key={CAPTCHA_KEY}&method=userrecaptcha&googlekey={sitekey}&pageurl={pageurl}&json=1"
        response = requests.get(url).json()
        if response["status"] != 1: return None  # Fixed typo (r -> response)
        req_id = response["request"]
        for _ in range(30):
            time.sleep(10)
            res = requests.get(f"http://2captcha.com/res.php?key={CAPTCHA_KEY}&action=get&id={req_id}&json=1").json()
            if res["status"] == 1: return res["request"]
    except Exception as e:
        print(f"[CAPTCHA ERROR] {e}")
        return None

def send_telegram(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}, timeout=10
        )
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

def run_bot():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")  # Fixed incomplete user-agent
    options.add_argument("--lang=es-ES")
    options.add_argument(f"--proxy-server={STATIC_PROXY}")
    service = Service(ChromeDriverManager().install())  # Added for browser startup fix
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://pakistan.blsspainvisa.com/book_appointment.php")  # Check if this URL works; alt: https://thespainvisa.com/book-appointment.php
        send_telegram("🚀 Bot started: Navigating to BLS Spain Visa Site")

        # Wait for form load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # Fill form (adjust IDs via dev tools if errors)
        wait.until(EC.element_to_be_clickable((By.ID, "center"))).send_keys("Islamabad")
        driver.find_element(By.ID, "visa_category_id").send_keys("SHORT TERM VISA")
        driver.find_element(By.ID, "passport_no").send_keys(PASSPORT_NO)
        driver.find_element(By.ID, "dob").send_keys(DOB)
        driver.find_element(By.ID, "name").send_keys(FIRST_NAME)
        driver.find_element(By.ID, "surname").send_keys(SURNAME)
        driver.find_element(By.ID, "email").send_keys(EMAIL)
        driver.find_element(By.ID, "phone").send_keys(PHONE)

        # Solve reCAPTCHA
        recaptcha_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha")))
        sitekey = recaptcha_div.get_attribute("data-sitekey")
        send_telegram("🔄 Solving reCAPTCHA...")
        g_response = solve_recaptcha(sitekey, driver.current_url)
        if not g_response:
            send_telegram("❌ CAPTCHA failed. Retry later.")
            return
        driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{g_response}";')

        # Submit form
        driver.find_element(By.ID, "submit").click()
        send_telegram("📤 Form submitted. Checking for slots...")
        time.sleep(5)
        if "No appointment slots are currently available" in driver.page_source.lower():
            send_telegram("🔍 No slots available.")
        else:
            send_telegram("🎉 Slot found! Manual OTP/email verification required. Go to pakistan.blsspainvisa.com to complete booking. Link: https://pakistan.blsspainvisa.com/book_appointment.php")
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(600)  # 10-minute checks to avoid bans

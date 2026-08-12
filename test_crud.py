import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    # Setup Chrome options for Headless mode (Wajib untuk GitHub Actions)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    
    # Prasyarat Login (Dilakukan di setiap worker secara independen)
    base_url = "http://localhost:8000"
    driver.get(f"{base_url}/login.php")
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("admin123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Tunggu sampai login berhasil dan diarahkan ke halaman index
    WebDriverWait(driver, 5).until(EC.url_contains("index.php"))
    
    yield driver
    
    # Teardown
    driver.quit()

# TEST CASE 1: Create Valid
def test_1_create_contact_valid(driver):
    driver.find_element(By.LINK_TEXT, "Add New Contact").click()
    driver.find_element(By.ID, "name").send_keys("Budi Santoso")
    driver.find_element(By.ID, "email").send_keys("budi@email.com")
    driver.find_element(By.ID, "phone").send_keys("08123456789")
    driver.find_element(By.ID, "title").send_keys("Staff")
    driver.find_element(By.CSS_SELECTOR, "input[value='Save']").click()
    
    assert "index.php" in driver.current_url

# TEST CASE 2: Create Invalid (Kosong)
def test_2_create_contact_empty(driver):
    driver.find_element(By.LINK_TEXT, "Add New Contact").click()
    driver.find_element(By.CSS_SELECTOR, "input[value='Save']").click()
    
    assert "create.php" in driver.current_url

# TEST CASE 3: Update Contact
def test_3_update_contact(driver):
    driver.get("http://localhost:8000/index.php")
    
    # Ambil baris terakhir agar tidak bentrok dengan test delete yang mengambil baris pertama
    driver.find_element(By.XPATH, "(//a[contains(text(), 'edit')])[last()]").click()
    
    phone_field = driver.find_element(By.ID, "phone")
    phone_field.clear()
    phone_field.send_keys("08999999999")
    
    driver.find_element(By.CSS_SELECTOR, "input[value='Update']").click()
    assert "index.php" in driver.current_url

# TEST CASE 4: Delete Contact
def test_4_delete_contact(driver):
    driver.get("http://localhost:8000/index.php")
    driver.find_element(By.XPATH, "//a[contains(text(), 'delete')]").click()
    
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert.accept()
    
    time.sleep(1)
    assert "index.php" in driver.current_url

# TEST CASE 5: Upload Invalid Format
def test_5_upload_profil_invalid(driver):
    driver.get("http://localhost:8000/profil.php")
    
    with open("dummy.txt", "w") as f:
        f.write("test invalid file")
    file_path = os.path.abspath("dummy.txt")
    
    driver.find_element(By.ID, "formFile").send_keys(file_path)
    driver.find_element(By.XPATH, "//button[text()='Change']").click()
    
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Ekstensi tidak diijinkan" in body_text
    os.remove("dummy.txt")

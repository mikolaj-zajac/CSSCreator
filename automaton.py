import os
import shutil
import time
import traceback

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
from selenium.webdriver.support.ui import Select
from ftplib import FTP

def open_chrome_with_profile():
    chrome_options = webdriver.ChromeOptions()
    profile_path = r'C:\Users\Cinek\AppData\Local\Google\Chrome\User Data'
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    chrome_options.add_argument("profile-directory=Profile 5")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def download_givi_file():
    givi_url = "https://sklep.bikespace.pl/xml?id=24&hash=e87d9fe95d790cd2c287ed70e32681368cf390718736554e008d564e54cb0f8e"
    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    givi_filename = os.path.join(download_folder, f"{date_today} givi.xml")
    response = requests.get(givi_url)
    if response.status_code == 200:
        with open(givi_filename, 'wb') as file:
            file.write(response.content)
        print(f"File {givi_filename} downloaded successfully.")
    else:
        print("Failed to download the givi file.")


def login_to_gmail_and_click_starred_link(driver):
    email_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQZTMLpRGvvXqzrDlcZMGGWBHxJ"
    driver.get(email_url)
    time.sleep(5)

    try:
        link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'shoeipolska.sharepoint.com')]"))
        )
        link_url = link.get_attribute("href")
        print(f"Link found: {link_url}")

        driver.get(link_url)
        print("Navigated to the link in the email.")
        time.sleep(5)

    except Exception as e:
        print(f"Error during Gmail interaction: {e}")


def download_shoei_file(driver):
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        more_actions_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='presentation' and @class='ms-List-cell' and @data-list-index='1']"))
        )
        more_actions_button.click()
        time.sleep(3)

        download_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//button[@type='button' and @role='menuitem' and @name='Pobierz' and @data-automationid='downloadCommand']"))
        )
        download_button.click()
        print("Download started.")

        time.sleep(5)

        date_today = datetime.now().strftime("%d%m")

        default_download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        downloaded_files = os.listdir(default_download_folder)
        downloaded_file = None
        for file in downloaded_files:
            if "shoei" in file.lower():
                downloaded_file = file
                break

        if downloaded_file:
            new_filename = f"{date_today} shoei.xml"
            old_file_path = os.path.join(default_download_folder, downloaded_file)
            new_file_path = os.path.join(download_folder, new_filename)
            shutil.move(old_file_path, new_file_path)
            print(f"File renamed and saved as {new_file_path}")
        else:
            print("Shoe file not found in the download folder.")

    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)

def login_and_download():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    chrome_options.add_argument("--headless")
    prefs = {"download.default_directory": download_folder}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://powerlink.powerbike.pl/B2BLogin.aspx")
    driver.find_element(By.ID, "LoginUserTX").send_keys("defender")
    driver.find_element(By.ID, "LoginPassTX").send_keys("defender199")
    driver.find_element(By.ID, "LoginZalogujX_BtnLabel").click()
    time.sleep(5)
    select_format = Select(driver.find_element(By.ID, "ctl00_MasterKartotekaPlikFormat"))
    select_format.select_by_value("1")
    time.sleep(2)
    manufacturers = [
        "AIROH", "ARAI", "BELL", "BROGER", "FOX", "HELD", "HJC", "IMX",
        "KRYPTONITE", "OZONE", "POD", "REBELHORN", "R&G RACING", "RST",
        "S100", "SP CONNECT", "SW MOTECH"
    ]
    for manufacturer in manufacturers:
        try:
            select_manufacturer = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_MasterKartotekaPlikProducent"))
            )
            select = Select(select_manufacturer)
            select.select_by_visible_text(manufacturer)
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ctl00_MasterKartotekaPlikPobierz_BtnLabel00"))
            )
            download_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error while processing {manufacturer}: {e}")
            continue
    driver.quit()

def shoei():
    driver = open_chrome_with_profile()
    if driver is None:
        print("Could not start Chrome. Exiting...")
        return
    login_to_gmail_and_click_starred_link(driver)
    download_shoei_file(driver)
    driver.quit()


def download_from_parts():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    chrome_options.add_argument("--headless")
    prefs = {"download.default_directory": download_folder}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.partseurope.eu/en/login")

    try:
        # Handle cookie notice if present
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'yes-to-all btn btn-primary btn-md save-information')]"))
            )
            driver.execute_script("arguments[0].click();", cookie_button)  # Use JavaScript to click
            time.sleep(2)

            save_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn btn-primary btn-md save-information')]"))
            )
            driver.execute_script("arguments[0].click();", save_button)  # Use JavaScript to click

            print("cookie notice handled")
            time.sleep(2)
        except Exception as e:
            print(f"Error handling cookie notice: {e}")

        driver.find_element(By.ID, "_email").send_keys("info@defender.net.pl")
        driver.find_element(By.ID, "_password").send_keys("Rf8ujq49!")
        print("Credentials entered")
        time.sleep(2)

        login_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn btn-primary btn-lg btn-icon')]"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(3)

        try:
            link_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/en/b2b/pricefiles')]"))
            )

            driver.execute_script("arguments[0].click();", link_element)
        except Exception as e:
            print(f"Error XD: {e}")

        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='search']"))
        )
        search_box.send_keys("pe_export_tab_ext_v4.txt")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        download_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/download/pricefile/979077')]"))
        )
        driver.execute_script("arguments[0].click();", download_link)  # Use JavaScript to click
        time.sleep(5)

        date_today = datetime.now().strftime("%d%m")
        default_download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        downloaded_files = os.listdir(default_download_folder)
        downloaded_file = None

        for file in downloaded_files:
            if "pe_export_tab_ext_v4" in file.lower():
                downloaded_file = file
                break

        if downloaded_file:
            new_filename = f"{date_today} pe_export_tab_ext_v4.txt"
            old_file_path = os.path.join(default_download_folder, downloaded_file)
            new_file_path = os.path.join(download_folder, new_filename)
            shutil.move(old_file_path, new_file_path)
            print(f"File saved as {new_file_path}")
        else:
            print("File not found in the download folder.")

    except Exception as e:
        print(f"Error during PartsEurope file download: {e}")
        print("Detailed error traceback:")
        print(traceback.format_exc())  # Print the detailed traceback to help debug the issue

    driver.quit()

def download_modeka():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://biketrade.pl/csv/")

    try:
        modeka_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'modeka.csv')]"))
        )
        file_url = modeka_link.get_attribute("href")
        date_today = datetime.now().strftime("%d%m")
        file_path = os.path.join(download_folder, f"{date_today} modeka.csv")

        response = requests.get(file_url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as: {file_path}")
        else:
            print("Failed to download Modeka CSV file.")

    except Exception as e:
        print(f"Error downloading Modeka file: {e}")

    driver.quit()

def download_olek():
    from datetime import datetime
    import os
    import requests

    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    url = "https://pim.olekmotocykle.com/xml?id=80&hash=100e47b1572543bd06e33cb9db1ba07436a08cda83bc32ffe7fe5daa4e7db588"
    file_path = os.path.join(download_folder, f"{date_today} olek.xml")

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File downloaded and saved as: {file_path}")
    else:
        print("Failed to download Olek file.")


def download_b2bike():
    ftp_url = "spidipolska.home.pl"
    ftp_user = "stany@b2bike.eu"
    ftp_pass = "B2bike123"
    remote_filepath = "/stany.xlsx"

    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    local_filepath = os.path.join(download_folder, f"{date_today} b2bike.xlsx")

    ftp = FTP(ftp_url)
    ftp.login(user=ftp_user, passwd=ftp_pass)

    with open(local_filepath, "wb") as local_file:
        ftp.retrbinary(f"RETR {remote_filepath}", local_file.write)

    ftp.quit()


def download_wilamt():
    url = "https://www.wmmotor.pl/hurtownia/pliki_download.php?login%3Dinfo@defender.net.pl%26key%3D8c645d4326caa74859ba22bc8338b6bb%26type%3Dpricelist%26lang%3Dpl%26curr%3Dpln"
    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    local_filepath = os.path.join(download_folder, f"{date_today} wilmat.xlsx")

    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filepath, "wb") as file:
            file.write(response.content)
        print(f"File {local_filepath} downloaded successfully.")
    else:
        print("Failed to download the wilmat file.")


def download_ridkp():
    url = "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=12"

    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    local_filepath = os.path.join(download_folder, f"{date_today} ridkp.xml")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            with open(local_filepath, "wb") as file:
                file.write(response.content)
            print(f"File {local_filepath} downloaded successfully.")
        else:
            print(f"Failed to download the ridkp file. Status Code: {response.status_code}")
            print(f"Response content: {response.text}")
    except Exception as e:
        print(f"Error downloading the ridkp file: {e}")


def download_riders():
    urls = [
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=16",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=9",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=19",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=22",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=25",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=62",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=70",
        "https://api.rider.com.pl/web-service.php?key=ZSAEy9IbziyejC9wXLJGtgAX6Ok7QlSY&grupa=7"
    ]

    date_today = datetime.now().strftime("%d%m")
    download_folder = os.path.join(os.path.expanduser("~"), "Desktop", "automation files")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for index, url in enumerate(urls, start=1):
        local_filepath = os.path.join(download_folder, f"{date_today} rider {index}.xml")

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                with open(local_filepath, "wb") as file:
                    file.write(response.content)
                print(f"File {local_filepath} downloaded successfully.")
            else:
                print(f"Failed to download from {url}. Status Code: {response.status_code}")
                print(f"Response content: {response.text}")
        except Exception as e:
            print(f"Error downloading from {url}: {e}")

def main():
    download_from_parts()
    shoei()
    download_givi_file()
    login_and_download()

    download_modeka()
    download_olek()
    download_b2bike()

    download_wilamt()
    download_ridkp()
    download_riders()

if __name__ == "__main__":
    main()

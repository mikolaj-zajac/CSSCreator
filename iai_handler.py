import os

import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

image_folder = "photos"

delete = [
    os.path.join(image_folder, "delete_1.jpg"),
    os.path.join(image_folder, "delete_2.jpg"),
    os.path.join(image_folder, "delete_3.jpg"),
    os.path.join(image_folder, "delete_4.jpg")
]

start = [
    os.path.join(image_folder, "add_button.jpg"),
    os.path.join(image_folder, "add_update_button.jpg"),
    os.path.join(image_folder, "file_select.jpg")
]

kp = [
    os.path.join(image_folder, "ok_button.jpg"),
    os.path.join(image_folder, "ok_button_2.jpg"),
    os.path.join(image_folder, "kp_button.jpg"),
    os.path.join(image_folder, "ok_button_3.jpg")
]

kp2 = [
    os.path.join(image_folder, "set_type.jpg"),
    os.path.join(image_folder, "type_kz.jpg"),
    os.path.join(image_folder, "type_ok_button.jpg")
]

kz = [
    os.path.join(image_folder, "ok_button.jpg"),
    os.path.join(image_folder, "ok_button_2.jpg"),
    os.path.join(image_folder, "kz_button.jpg"),
    os.path.join(image_folder, "ok_button_3.jpg")
]
kz2 = [
    os.path.join(image_folder, "set_type.jpg"),
    os.path.join(image_folder, "type_kp.jpg"),
    os.path.join(image_folder, "type_ok_button.jpg")
]

finish = [
    os.path.join(image_folder, "set_type.jpg"),
    os.path.join(image_folder, "type_availability.jpg"),
    os.path.join(image_folder, "type_set_separators.jpg"),
    os.path.join(image_folder, "type_ok_button.jpg"),
    os.path.join(image_folder, "set_type.jpg"),
    os.path.join(image_folder, "type_id.jpg"),
    os.path.join(image_folder, "type_set_separators.jpg"),
    os.path.join(image_folder, "type_ok_button.jpg"),
    os.path.join(image_folder, "save_button.jpg")
]

def select_file(name):
    pyautogui.write('automation files')
    pyautogui.press('enter')
    time.sleep(0.5)

    pyautogui.write('update')
    pyautogui.press('enter')
    time.sleep(0.5)

    pyautogui.write(name+".csv")
    pyautogui.press('enter')
    time.sleep(1)

def click_images(image_list, delay=3):
    for image in image_list:
        time.sleep(delay)
        try:
            location = pyautogui.locateCenterOnScreen(image, confidence=0.75)
            if location:
                pyautogui.moveTo(location)
                pyautogui.click()

        except Exception as e:
            print(f"Error processing {image}: {e}")

def close_iai(delay=3):
    time.sleep(delay)
    image = os.path.join(image_folder, "close.jpg")
    try:
        location = pyautogui.locateCenterOnScreen(image, confidence=0.99)
        if location:
            pyautogui.moveTo(location)
            pyautogui.click()
    except Exception as e:
        print(f"Error processing {image}: {e}")

def start_process():
    click_images(start)

def delete_process():
    click_images(delete)

def kp_process_1():
    click_images(kp)

def kp_process_2():
    click_images(kp2)

def kz_process_1():
    click_images(kz)

def kz_process_2():
    click_images(kz2)

def finish_process():
    click_images(finish)

def open_iai():
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("iai", interval=0.1)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(30)

def set_warehouse_management_external():
    with open("password", "r") as file:
        password = file.read().strip()

    driver = webdriver.Chrome()
    driver.get("https://defender.net.pl/panel/index.php")
    time.sleep(2)

    login_input = driver.find_element(By.ID, "panel_login")
    login_input.send_keys("Serwer")
    login_input.send_keys(Keys.RETURN)

    password_input = driver.find_element(By.ID, "panel_password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    driver.get("https://defender.net.pl/panel/stocks.php")

    select = driver.find_element(By.ID, "fg_label_stockInfo[mainStockSystem]1")
    select.click()
    time.sleep(0.5)
    button = driver.find_element(By.ID, "stocksConfigSave")
    button.click()

    driver.quit()

def set_warehouse_management_internal():
    with open("password", "r") as file:
        password = file.read().strip()

    driver = webdriver.Chrome()
    driver.get("https://defender.net.pl/panel/index.php")
    time.sleep(2)

    login_input = driver.find_element(By.ID, "panel_login")
    login_input.send_keys("Serwer")
    login_input.send_keys(Keys.RETURN)

    password_input = driver.find_element(By.ID, "panel_password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    driver.get("https://defender.net.pl/panel/stocks.php")

    select = driver.find_element(By.ID, "fg_label_stockInfo[mainStockSystem]0")
    select.click()
    time.sleep(0.5)
    button = driver.find_element(By.ID, "stocksConfigSave")
    button.click()
    driver.quit()

def all_of_kp():
    start_process()
    select_file("kp")
    kp_process_1()
    time.sleep(120)
    kp_process_2()
    finish_process()

def all_of_kz():
    start_process()
    select_file("kz")
    kz_process_1()
    time.sleep(120)
    kz_process_2()
    finish_process()

def delete_files():
    delete_process()
    time.sleep(2)
    delete_process()

if __name__ == "__main__":
    # open_iai()
    # all_of_kp()
    # time.sleep(300)
    # all_of_kz()
   close_iai()

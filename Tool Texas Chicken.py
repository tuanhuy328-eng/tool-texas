import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# CẤU HÌNH THƯ MỤC LƯU ẢNH TRANG CUỐI 
SCREENSHOT_DIR = "./ket_qua_khao_sat"

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)
    print(f"📁 Đã tạo thư mục lưu kết quả tại: {SCREENSHOT_DIR}")

# KHỞI TẠO SELENIUM 
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

next_btn_xpath = (
    "//button[contains(., 'Next')] | //button[contains(., 'Finish')] |"
    " //*[@id='forward_main-pager'] | //input[@value='Next'] |"
    " //input[@value='Finish'] | //button[contains(., 'Begin Survey')]"
)


# CÁC HÀM TƯƠNG TÁC 
def click_js(xpath, wait_time=10):
    """Click phần tử bằng JS, chờ element clickable thay vì chỉ present."""
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Lỗi khi click JS: {xpath[:50]}...")
        return False


def select_all_js(value):
    """Chọn tất cả element khớp với value, tối ưu delay."""
    #Thời gian để chuyển trang và render các lựa chọn mới
    time.sleep(0.3)
    xpath = (
        f"//label[contains(normalize-space(.), '{value}')] |"
        f" //span[contains(normalize-space(.), '{value}')] | //input[@value='{value}']"
    )
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        if not elements:
            print(f"  --> Cảnh báo: Không tìm thấy lựa chọn: {value}")

        for el in elements:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            driver.execute_script("arguments[0].click();", el)
            time.sleep(0.05)  # Giảm từ 0.2s → 0.05s
    except Exception as e:
        print(f"  --> Lỗi select_all_js('{value}'): {e}")


def capture_final_page():
    """Chụp ảnh màn hình trang cuối cùng thành công."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SCREENSHOT_DIR, f"hoan_thanh_{timestamp}.png")
        time.sleep(0.5)
        driver.save_screenshot(file_path)
        print(f"\n📸 ĐÃ CHỤP ẢNH TRANG CUỐI THÀNH CÔNG: {file_path}")
    except Exception as e:
        print(f"❌ Không thể chụp ảnh trang cuối: {e}")


#Bắt đầu quy trình khảo sát
try:
    # Trang 1: Nhập thông tin cơ bản
    driver.get("https://www.texaschickensurvey-sg.com")
    print("Trang 1: Đang nhập thông tin...")

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='q_ctc_restaurant_num_txt']"))
    ).send_keys("10869")
    driver.find_element(By.CSS_SELECTOR, "input[name*='q_ctc_order_number_txt']").send_keys("1")

    target_date = "06/22/2026"
    date_input = driver.find_element(By.CSS_SELECTOR, "input[name*='q_ctc_order_date']")
    driver.execute_script(f"arguments[0].value = '{target_date}';", date_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", date_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('blur'))", date_input)
    print(f"Đã nhập ngày: {target_date}")

    click_js(next_btn_xpath)

    # Trang 2–4: Lựa chọn đơn giản
    for page_num, choice in enumerate(["Take-Away", "At the counter", "Before 11:00 AM"], 2):
        print(f"Trang {page_num}: Chọn '{choice}'...")
        select_all_js(choice)
        click_js(next_btn_xpath)

    # Trang 5–10: Các bước đánh giá
    rating_steps = [
        ("5",                   "Trang 5:  Overall Satisfaction"),
        ("Yes",                 "Trang 6:  Greeted/Order repeated/Thanked"),
        ("5",                   "Trang 7:  Taste/Accuracy/Temperature"),
        ("Less than 3 minutes", "Trang 8:  Wait time"),
        ("No",                  "Trang 9:  Experience a problem"),
        ("5",                   "Trang 10: Likelihood to return/recommend"),
    ]
    for value, msg in rating_steps:
        print(msg)
        select_all_js(value)
        click_js(next_btn_xpath)

    # Trang 11: Nhận xét (bỏ qua)
    print("Trang 11: Nhận xét (Bỏ qua)...")
    click_js(next_btn_xpath)

    # Trang 12–22: Các câu hỏi chi tiết
    detail_steps = [
        (["Individual Combo"],                          "Trang 12: Loại combo"),
        (["Order Bone-In Original Chicken"],            "Trang 13: Món cụ thể"),
        (["Once"],                                      "Trang 14: Tần suất ghé thăm"),
        (["No"],                                        "Trang 15: First experience?"),
        (["Less than a month ago"],                     "Trang 16: Last time visited"),
        (["Prior positive experience"],                 "Trang 17: Primary reason"),
        (["Prior positive experience", "Yes", "5"],     "Trang 18: Limited Time Offer"),
        (["5"],                                         "Trang 19: LTO next 30 days"),
        (["Prefer not to answer"],                      "Trang 20: Indicate your..."),
        (["No"],                                        "Trang 21: Staff member"),
        (["No"],                                        "Trang 22: Email address"),
    ]
    for choices, msg in detail_steps:
        print(f"{msg}...")
        for choice in choices:
            select_all_js(choice)
        click_js(next_btn_xpath)

    # --- CHỤP ẢNH KHI HOÀN THÀNH ---
    capture_final_page()

except Exception as e:
    print(f"❌ Có lỗi xảy ra: {e}")

finally:
    input("\nNhấn Enter để đóng trình duyệt...")
    driver.quit()
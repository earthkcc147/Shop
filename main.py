import os
import json
import requests
from dotenv import load_dotenv

# โหลดข้อมูลจากไฟล์ .env
load_dotenv()

# อ่านข้อมูลจาก .env
API_URL = os.getenv('API_URL')
USERS = json.loads(os.getenv('USERS'))  # แปลงค่า USERS เป็น list ของ dictionary

# ฟังก์ชันสำหรับล็อคอิน
def login(username, password):
    user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    if user:
        print(f"ล็อคอินสำเร็จสำหรับ {username}")
        return user
    else:
        print("การล็อคอินล้มเหลว กรุณาตรวจสอบชื่อผู้ใช้และรหัสผ่าน.")
        return None

# ฟังก์ชันสำหรับเพิ่มคำสั่งซื้อ
def add_order(user, service_id):
    api_key = user['Api_key']
    link = input("กรุณากรอกลิงก์สำหรับการสั่งซื้อ: ")
    try:
        quantity = int(input("กรุณากรอกจำนวนที่ต้องการ: "))
    except ValueError:
        print("จำนวนไม่ถูกต้อง กรุณากรอกตัวเลข.")
        return

    params = {
        'key': api_key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    
    response = requests.post(f'{API_URL}/order', params=params)
    if response.status_code == 200:
        response_data = response.json()
        if 'order' in response_data:
            print(f"คำสั่งซื้อสำเร็จ! หมายเลขคำสั่งซื้อ: {response_data['order']}")
        else:
            print(f"เกิดข้อผิดพลาด: {response_data}")
    else:
        print(f"ไม่สามารถสั่งซื้อได้: {response.status_code}")

# ฟังก์ชันสำหรับแสดงข้อมูลบริการ
def show_service_data(user, platform):
    services = user['products'].get(platform, [])
    print(f"\nข้อมูลบริการสำหรับ {platform}:")
    for idx, service_id in enumerate(services, 1):
        print(f"{idx}. Service ID: {service_id}")
    
    try:
        choice = int(input(f"\nกรุณากรอกหมายเลข Service (1-{len(services)}): "))
        if 1 <= choice <= len(services):
            service_id = services[choice - 1]
            print(f"\nคุณเลือก Service ID: {service_id}")
            add_order(user, service_id)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_service_data(user, platform)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_service_data(user, platform)

# ฟังก์ชันสำหรับแสดงเมนูแพลตฟอร์ม
def show_platform_menu(user):
    print("\nกรุณาเลือกแพลตฟอร์มที่ต้องการจัดการบริการ:")
    platforms = user['products'].keys()
    for idx, platform in enumerate(platforms, 1):
        print(f"{idx}. {platform}")
    
    try:
        choice = int(input(f"\nกรุณากรอกหมายเลข (1-{len(platforms)}): "))
        if 1 <= choice <= len(platforms):
            platform = list(platforms)[choice - 1]
            print(f"\nคุณเลือกแพลตฟอร์ม {platform}.\n")
            show_service_data(user, platform)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_platform_menu(user)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_platform_menu(user)

# ฟังก์ชันหลัก
def main():
    print("ยินดีต้อนรับสู่ระบบจัดการบริการ!")
    print("กรุณาล็อคอินเพื่อดำเนินการต่อ")
    
    username = input("กรุณากรอกชื่อผู้ใช้: ")
    password = input("กรุณากรอกรหัสผ่าน: ")
    
    user = login(username, password)
    if user:
        show_platform_menu(user)

if __name__ == '__main__':
    main()
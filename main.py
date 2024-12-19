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

    # การส่งคำขอ POST ไปยัง API
    params = {
        'key': api_key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    
    # ส่งคำขอ POST ไปยัง API_URL
    try:
        response = requests.post(f'{API_URL}', data=params)
        response.raise_for_status()  # ตรวจสอบว่าไม่มีข้อผิดพลาด HTTP
        
        # การตรวจสอบการตอบกลับ
        response_data = response.json()
        if 'order' in response_data:
            print(f"คำสั่งซื้อสำเร็จ! หมายเลขคำสั่งซื้อ: {response_data['order']}")
        else:
            print(f"เกิดข้อผิดพลาดในการสร้างคำสั่งซื้อ: {response_data}")
    except requests.exceptions.RequestException as e:
        print(f"ไม่สามารถเชื่อมต่อกับ API ได้: {e}")
    except ValueError:
        print("ตอบกลับจาก API ไม่ถูกต้อง.")

# ฟังก์ชันสำหรับดึงข้อมูลบริการจาก API
def get_services(user):
    api_key = user['Api_key']
    params = {
        'key': api_key,
        'action': 'services'
    }
    
    try:
        response = requests.post(f'{API_URL}', data=params)
        response.raise_for_status()
        services = response.json()
        return services
    except requests.exceptions.RequestException as e:
        print(f"ไม่สามารถดึงข้อมูลบริการได้: {e}")
        return []

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
            show_service_details(user, service_id)  # แสดงรายละเอียดของบริการที่เลือก
            add_order(user, service_id)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_service_data(user, platform)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_service_data(user, platform)

# ฟังก์ชันสำหรับแสดงรายละเอียดของบริการ
def show_service_details(user, service_id):
    services = get_services(user)  # ดึงข้อมูลบริการจาก API
    service = next((s for s in services if s['service'] == service_id), None)
    
    if service:
        print(f"\nรายละเอียดของบริการ {service_id}:")
        print(f"ชื่อบริการ: {service['name']}")
        print(f"ประเภท: {service['type']}")
        print(f"หมวดหมู่: {service['category']}")
        print(f"อัตรา: {service['rate']}")
        print(f"ขั้นต่ำ: {service['min']}")
        print(f"สูงสุด: {service['max']}")
        print(f"เติมใหม่ได้: {'ใช่' if service['refill'] else 'ไม่ใช่'}")
        print(f"ยกเลิกได้: {'ใช่' if service['cancel'] else 'ไม่ใช่'}")
    else:
        print(f"ไม่พบข้อมูลบริการที่มี Service ID: {service_id}")

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
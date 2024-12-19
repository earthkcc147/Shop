import os
import json
import requests
from dotenv import load_dotenv

# โหลดข้อมูลจากไฟล์ .env
load_dotenv()

# อ่านข้อมูลจาก .env
API_URL = os.getenv('API_URL')  # อ่าน API URL
USERS = json.loads(os.getenv('USERS'))  # อ่าน USERS จาก .env และแปลงเป็น list

# ฟังก์ชันสำหรับล็อคอิน
def login(username, password):
    user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    if user:
        print(f"ล็อคอินสำเร็จสำหรับ {username}")
        return user
    else:
        print(f"การล็อคอินล้มเหลวสำหรับ {username}")
        return None

# ฟังก์ชันสำหรับดึงข้อมูลสินค้าจาก API
def get_service_data(user):
    api_key = user['Api_key']  # ใช้ API Key ของผู้ใช้
    params = {
        'key': api_key,
        'action': 'services'
    }
    
    # ส่งคำขอ POST ไปยัง API
    response = requests.post(f'{API_URL}/service', data=params)
    
    if response.status_code == 200:
        service_data = response.json()
        print("ข้อมูลสินค้า:")
        for item in service_data:
            print(f"Service ID: {item['service']}")
            print(f"ชื่อสินค้า: {item['name']}")
            print(f"ประเภท: {item['type']}")
            print(f"หมวดหมู่: {item['category']}")
            print(f"อัตรา: {item['rate']} บาท")
            print(f"ขั้นต่ำ: {item['min']}")
            print(f"สูงสุด: {item['max']}")
            print(f"เติมเงินได้: {'ใช่' if item['refill'] else 'ไม่ใช่'}")
            print(f"ยกเลิกได้: {'ใช่' if item['cancel'] else 'ไม่ใช่'}")
            print("-" * 50)
        return service_data
    else:
        print(f"ไม่สามารถดึงข้อมูลสินค้าได้: {response.status_code}")
        return None

# ฟังก์ชันสำหรับสั่งซื้อสินค้า
def place_order(user, service_id, link, quantity):
    api_key = user['Api_key']
    params = {
        'key': api_key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    
    response = requests.post(f'{API_URL}/order', data=params)
    
    if response.status_code == 200:
        order_data = response.json()
        print(f"คำสั่งซื้อสำเร็จ! หมายเลขคำสั่งซื้อ: {order_data['order']}")
    else:
        print(f"ไม่สามารถเพิ่มคำสั่งซื้อได้: {response.status_code}")

# ฟังก์ชันหลัก
def main():
    print("ระบบจัดการบริการ")
    username = input("ชื่อผู้ใช้: ")
    password = input("รหัสผ่าน: ")
    
    user = login(username, password)
    if user:
        print("\nดึงข้อมูลสินค้า...")
        services = get_service_data(user)
        
        if services:
            # เลือกสินค้า
            try:
                service_id = int(input("กรุณาเลือก Service ID: "))
                selected_service = next((s for s in services if s['service'] == service_id), None)
                
                if selected_service:
                    link = input("กรุณากรอกลิงก์สำหรับคำสั่งซื้อ: ")
                    quantity = int(input("กรุณากรอกจำนวนที่ต้องการสั่งซื้อ: "))
                    
                    # ตรวจสอบจำนวนที่เลือกอยู่ในช่วงขั้นต่ำและสูงสุด
                    if selected_service['min'] <= quantity <= selected_service['max']:
                        place_order(user, service_id, link, quantity)
                    else:
                        print(f"จำนวนต้องอยู่ระหว่าง {selected_service['min']} และ {selected_service['max']}")
                else:
                    print("Service ID ไม่ถูกต้อง")
            except ValueError:
                print("กรุณากรอก Service ID ที่ถูกต้อง")
    else:
        print("ไม่สามารถล็อคอินได้")

if __name__ == "__main__":
    main()
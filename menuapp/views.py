from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class MenuFlyweight:
    """Intrinsic State: ข้อมูลที่ใช้ร่วมกันและไม่เปลี่ยนแปลง (รูปภาพ, คำอธิบาย)"""
    def __init__(self, name, description, price, image_url):
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url

class MenuFactory:
    """Factory สำหรับจัดการ Object ของเมนูอาหาร"""
    _menus = {}
    _creation_count = 0

    @classmethod
    def get_menu(cls, name, description, price, image_url):
        if name not in cls._menus:
            cls._creation_count += 1
            cls._menus[name] = MenuFlyweight(name, description, price, image_url)
        return cls._menus[name]
    
    @classmethod
    def get_menu_by_name(cls, name):
        return cls._menus.get(name)
    
    @classmethod
    def get_creation_count(cls):
        return cls._creation_count

class CustomerOrder:
    """Extrinsic State: ข้อมูลออเดอร์ที่เปลี่ยนไปตามบริบทของลูกค้าแต่ละโต๊ะ"""
    def __init__(self, table_number):
        self.table_number = table_number
        self.items = []

    def add_item(self, menu_flyweight):
        self.items.append(menu_flyweight)
        
    def get_total_price(self):
        return sum(item.price for item in self.items)

class OrderManager:
    """จัดการออเดอร์รวมของทุกโต๊ะ"""
    _orders = {}

    @classmethod
    def get_or_create_order(cls, table_number):
        if table_number not in cls._orders:
            cls._orders[table_number] = CustomerOrder(table_number)
        return cls._orders[table_number]


# สร้างแคตตาล็อกตั้งต้น
def init_catalog():
    return [
        MenuFactory.get_menu("ต้มยำกุ้ง (Tom Yum)", "ต้มยำกุ้งน้ำข้น รสจัดจ้าน กุ้งตัวโตๆ", 250, "https://images.unsplash.com/photo-1548943487-a2e4f43b4850?auto=format&fit=crop&w=800&q=80"),
        MenuFactory.get_menu("ผัดไทยกุ้งสด (Pad Thai)", "เส้นจันท์เหนียวนุ่ม ผัดซอสสูตรพิเศษ", 120, "https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=800&q=80"),
        MenuFactory.get_menu("แกงเขียวหวาน (Green Curry)", "แกงเขียวหวานไก่ หอมกลิ่นกะทิและเครื่องแกง", 150, "https://images.unsplash.com/photo-1548946522-4a313e8972a4?auto=format&fit=crop&w=800&q=80"),
        MenuFactory.get_menu("ข้าวเหนียวมะม่วง (Mango Sticky Rice)", "ข้าวเหนียวมูนกะทิสด ทานคู่กับมะม่วงน้ำดอกไม้สุก", 100, "https://images.unsplash.com/photo-1605697200762-23c310433e14?auto=format&fit=crop&w=800&q=80"),
        MenuFactory.get_menu("ส้มตำไทย (Som Tum)", "มะละกอกรอบ รสชาติเปรี้ยวหวานลงตัว", 80, "https://images.unsplash.com/photo-1564834724105-918b73d1b9e0?auto=format&fit=crop&w=800&q=80"),
        MenuFactory.get_menu("ชาเย็น (Thai Iced Tea)", "ชาไทยสีส้ม หอมหวานมัน ชื่นใจ", 60, "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=800&q=80")
    ]

# เก็บแคตตาล็อกไว้ในตัวแปรแบบ Global (เพื่อทำระบบ CRUD แบบ In-memory)
catalog_items = init_catalog()

def welcome(request):
    """หน้าแรกให้เลือกว่าเป็นลูกค้าหรือพนักงาน"""
    return render(request, 'welcome.html')

def customer_menu(request):
    """หน้าสำหรับลูกค้าดูและสั่งอาหาร"""
    table_num = request.GET.get('table', '1')
    
    try:
        users = int(request.GET.get('users', 1))
    except ValueError:
        users = 1

    objects_created = MenuFactory.get_creation_count()
    num_items = len(catalog_items)
    
    objects_without_flyweight = num_items * users
    memory_used_flyweight = objects_created * 2.5 
    memory_without_flyweight = objects_without_flyweight * 2.5
    memory_saved = memory_without_flyweight - memory_used_flyweight

    context = {
        'items': catalog_items,
        'table': table_num,
        'users': users,
        'objects_created': objects_created,
        'objects_without_flyweight': "{:,}".format(objects_without_flyweight),
        'memory_used_flyweight': "{:,.1f}".format(memory_used_flyweight),
        'memory_without_flyweight': "{:,.1f}".format(memory_without_flyweight),
        'memory_saved': "{:,.1f}".format(memory_saved),
    }
    return render(request, 'index.html', context)

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        table_num = request.POST.get('table', 'General')
        item_name = request.POST.get('item_name')
        
        menu_item = MenuFactory.get_menu_by_name(item_name)
        if menu_item:
            order = OrderManager.get_or_create_order(table_num)
            order.add_item(menu_item)
            
            return JsonResponse({
                'status': 'success', 
                'message': f'สั่ง {item_name} สำเร็จ!',
                'total_items': len(order.items),
                'total_price': order.get_total_price(),
                'table': table_num
            })
        return JsonResponse({'status': 'error', 'message': 'ไม่พบเมนูอาหาร'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def staff_login(request):
    """ระบบ Login ของพนักงาน"""
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == '051147':
            response = redirect('staff_dashboard')
            response.set_cookie('staff_auth', '1')
            return response
        else:
            return render(request, 'welcome.html', {'error': 'รหัสผ่านไม่ถูกต้อง'})
    return redirect('welcome')

@csrf_exempt
def staff_dashboard(request):
    """หน้า CRUD เมนูอาหาร และดูออเดอร์ลูกค้า"""
    if request.COOKIES.get('staff_auth') != '1':
        return redirect('welcome')
    
    global catalog_items
    
    # ระบบ CRUD (เพิ่ม/ลบ)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            desc = request.POST.get('description')
            price = int(request.POST.get('price', 0))
            img = request.POST.get('image_url')
            
            # การเพิ่มเมนู จะเรียกใช้ Flyweight Factory ถ้าเคยมีรูป/ชื่อนี้แล้วก็จะไม่สร้างใหม่
            new_item = MenuFactory.get_menu(name, desc, price, img)
            if new_item not in catalog_items:
                catalog_items.append(new_item)
                
        elif action == 'delete':
            name = request.POST.get('name')
            catalog_items = [item for item in catalog_items if item.name != name]
            if name in MenuFactory._menus:
                del MenuFactory._menus[name]
        
        elif action == 'reset':
            MenuFactory._menus.clear()
            MenuFactory._creation_count = 0
            catalog_items = init_catalog()

    # เตรียมข้อมูลออเดอร์ไปโชว์
    orders_data = []
    for table, order in OrderManager._orders.items():
        if order.items:
            orders_data.append({
                'table': table,
                'total_price': order.get_total_price(),
                'item_names': [item.name for item in order.items]
            })
            
    context = {
        'menus': catalog_items,
        'orders': orders_data
    }
    return render(request, 'staff.html', context)
    
def staff_logout(request):
    response = redirect('welcome')
    response.delete_cookie('staff_auth')
    return response

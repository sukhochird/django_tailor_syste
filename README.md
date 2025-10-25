# Оёдлын Удирдлагын Систем (Tailor Management System)

Энэ нь React-аас Django руу хөрвүүлсэн оёдлын удирдлагын систем юм.

## Онцлогууд

- **Захиалгын удирдлага**: Захиалга үүсгэх, засах, хянах
- **Үйлчлүүлэгчдийн удирдлага**: Үйлчлүүлэгчдийн мэдээлэл хадгалах
- **Ажилтнуудын удирдлага**: Оёдолчин, эсгүүрчин, өмдний оёдолчдын мэдээлэл
- **Материалын удирдлага**: Материалын нөөц, үнэ, нийлүүлэгч
- **Тайлан**: Системийн статистик болон тайлан
- **Үйл явцын хяналт**: Захиалгын үйл явцыг алхам алхамаар хянах

## Суулгах заавар

### 1. Системийн шаардлага
- Python 3.8+
- Django 5.2+

### 2. Суулгах
```bash
# Virtual environment үүсгэх
python -m venv venv

# Virtual environment идэвхжүүлэх
source venv/bin/activate  # macOS/Linux
# эсвэл
venv\Scripts\activate  # Windows

# Dependencies суулгах
pip install django djangorestframework django-cors-headers pillow

# Database migration хийх
python manage.py makemigrations
python manage.py migrate

# Superuser үүсгэх
python manage.py createsuperuser

# Sample data үүсгэх (сонголт)
python create_sample_data.py
```

### 3. Сервер ажиллуулах
```bash
python manage.py runserver
```

Систем http://127.0.0.1:8000/ хаяг дээр ажиллана.

## Хэрэглэх заавар

### Нэвтрэх
- URL: http://127.0.0.1:8000/admin/
- Username: admin
- Password: admin123

### Үндсэн функцууд

1. **Хяналтын самбар**: Системийн ерөнхий статистик
2. **Захиалга**: Захиалга үүсгэх, засах, хянах
3. **Үйлчлүүлэгчид**: Үйлчлүүлэгчдийн мэдээлэл
4. **Ажилтнууд**: Ажилтнуудын мэдээлэл
5. **Материалууд**: Материалын нөөц
6. **Тайлан**: Төрөл бүрийн тайлан

## Техникийн мэдээлэл

### Apps
- `orders`: Захиалгын удирдлага
- `customers`: Үйлчлүүлэгчдийн удирдлага  
- `employees`: Ажилтнуудын удирдлага
- `materials`: Материалын удирдлага
- `reports`: Тайлангийн удирдлага

### Models
- **Customer**: Үйлчлүүлэгчдийн мэдээлэл
- **Employee**: Ажилтнуудын мэдээлэл
- **Material**: Материалын мэдээлэл
- **Order**: Захиалгын мэдээлэл
- **ProcessStep**: Үйл явцын алхам
- **OrderRating**: Захиалгын үнэлгээ
- **Report**: Тайлангийн мэдээлэл

### Templates
- `base.html`: Үндсэн template
- `dashboard.html`: Хяналтын самбар
- Бусад app-уудын templates

## Sample Data

Системд sample data байгаа бөгөөд дараах мэдээлэл орсон байна:

- 4 үйлчлүүлэгч (VIP болон энгийн)
- 5 ажилтан (оёдолчин, эсгүүрчин, өмдний оёдолчин)
- 4 материал
- 3 захиалга (өөр өөр статустай)

## API

REST API боломжтой бөгөөд дараах endpoints ашиглаж болно:

- `/api/orders/` - Захиалгын API
- `/api/customers/` - Үйлчлүүлэгчдийн API
- `/api/employees/` - Ажилтнуудын API
- `/api/materials/` - Материалын API

## Хөгжүүлэлт

### Нэмэлт функц нэмэх
1. Model үүсгэх
2. View үүсгэх
3. URL pattern нэмэх
4. Template үүсгэх
5. Form үүсгэх (шаардлагатай бол)

### Database өөрчлөх
```bash
python manage.py makemigrations
python manage.py migrate
```

## Тусламж

Асуудал гарвал:
1. Django documentation шалгах
2. Error message-ийг сайтар унших
3. Stack trace-ийг шалгах

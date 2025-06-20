from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import get_db_connection
from utils import is_admin


class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    username = State()


# Create user menu
def get_user_menu():
    keyboard = [
        [KeyboardButton(text="/start"), KeyboardButton(text="/stop")],
        [KeyboardButton(text="/register")],
        [KeyboardButton(text="/list_products"), KeyboardButton(text="/search")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, selective=True)


def get_admin_menu():
    keyboard = [
        [KeyboardButton(text="/start"), KeyboardButton(text="/stop")],
        [KeyboardButton(text="/register")],
        [KeyboardButton(text="/add_category"), KeyboardButton(text="/add_product")],
        [KeyboardButton(text="/delete_product"), KeyboardButton(text="/update_product")],
        [KeyboardButton(text="/list_products"), KeyboardButton(text="/search")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, selective=True)


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(stop, Command(commands=["stop"]))
    dp.message.register(register, Command(commands=["register"]))
    dp.message.register(get_first_name, RegistrationStates.first_name)
    dp.message.register(get_last_name, RegistrationStates.last_name)
    dp.message.register(get_phone_number, RegistrationStates.phone_number)
    dp.message.register(get_username, RegistrationStates.username)
    dp.message.register(add_category, Command(commands=["add_category"]))
    dp.message.register(add_product, Command(commands=["add_product"]))
    dp.message.register(delete_product, Command(commands=["delete_product"]))
    dp.message.register(update_product, Command(commands=["update_product"]))
    dp.message.register(list_products, Command(commands=["list_products"]))
    dp.message.register(search, Command(commands=["search"]))


async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "noma'lum"

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (id, username, role) VALUES (?, ?, ?)",
                  (user_id, username, 'user'))
        conn.commit()

    conn.close()


    menu = get_admin_menu() if is_admin(user_id) else get_user_menu()

    await message.answer(
        "Xush kelibsiz! Quyidagi buyruqlardan foydalaning:\n"
        "/start - Menyuni qayta ko'rsatish\n"
        "/stop - Menyuni o'chirish\n"
        "/register - Ro'yxatdan o'tish\n"
        "/add_category <nomi> - Yangi kategoriya qo'shish (admin)\n"
        "/add_product <nomi> <kategoriya_id> <narx> - Mahsulot qo'shish (admin)\n"
        "/delete_product <id> - Mahsulot o'chirish (admin)\n"
        "/update_product <id> <nomi> <kategoriya_id> <narx> - Mahsulot o'zgartirish (admin)\n"
        "/list_products - Mahsulotlarni ko'rish\n"
        "/search <so'z> - Mahsulot qidirish",
        reply_markup=menu
    )


async def stop(message: types.Message):
    await message.answer("Menyu o'chirildi. Qayta boshlash uchun /start yuboring.",
                         reply_markup=types.ReplyKeyboardRemove())


async def register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if c.fetchone():
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz!",
                             reply_markup=get_admin_menu() if is_admin(user_id) else get_user_menu())
        conn.close()
        return

    conn.close()

    await state.set_state(RegistrationStates.first_name)
    await message.answer("Iltimos, ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())


async def get_first_name(message: types.Message, state: FSMContext):
    first_name = message.text.strip()
    if not first_name.isalpha():
        await message.answer("Iltimos, faqat harflardan iborat ismingizni kiriting!")
        return

    await state.update_data(first_name=first_name)
    await state.set_state(RegistrationStates.last_name)
    await message.answer("Iltimos, familiyangizni kiriting:")


async def get_last_name(message: types.Message, state: FSMContext):
    last_name = message.text.strip()
    if not last_name.isalpha():
        await message.answer("Iltimos, faqat harflardan iborat familiyangizni kiriting!")
        return

    await state.update_data(last_name=last_name)
    await state.set_state(RegistrationStates.phone_number)
    await message.answer("Iltimos, telefon raqamingizni kiriting (masalan: +998901234567):")


async def get_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text.strip()
    if not phone_number.startswith("+") or not phone_number[1:].isdigit() or len(phone_number) < 10:
        await message.answer("Iltimos, to'g'ri telefon raqamini kiriting (masalan: +998901234567)!")
        return

    await state.update_data(phone_number=phone_number)
    await state.set_state(RegistrationStates.username)
    await message.answer("Iltimos, username kiriting (masalan: @username):")


async def get_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@"):
        await message.answer("Iltimos, username @ bilan boshlanishi kerak (masalan: @username)!")
        return

    user_data = await state.get_data()
    first_name = user_data["first_name"]
    last_name = user_data["last_name"]
    phone_number = user_data["phone_number"]
    user_id = message.from_user.id

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO users (id, username, role, first_name, last_name, phone_number) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, username, 'user', first_name, last_name, phone_number)
    )
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer(
        f"Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n"
        f"Ism: {first_name}\nFamiliya: {last_name}\nTelefon: {phone_number}\nUsername: {username}",
        reply_markup=get_user_menu()
    )


async def add_category(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Faqat adminlar kategoriya qo'sha oladi!", reply_markup=get_user_menu())
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Iltimos, kategoriya nomini kiriting!", reply_markup=get_admin_menu())
        return

    name = args[1]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    await message.answer(f"Kategoriya '{name}' qo'shildi!", reply_markup=get_admin_menu())


async def add_product(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Faqat adminlar mahsulot qo'sha oladi!", reply_markup=get_user_menu())
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer("Iltimos, mahsulot nomi, kategoriya ID va narxini kiriting!",
                             reply_markup=get_admin_menu())
        return

    try:
        name = args[1]
        category_id = int(args[2])
        price = float(args[3])

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO products (name, category_id, price) VALUES (?, ?, ?)",
                  (name, category_id, price))
        conn.commit()
        conn.close()
        await message.answer(f"Mahsulot '{name}' qo'shildi!", reply_markup=get_admin_menu())
    except ValueError:
        await message.answer("Kategoriya ID va narx raqam bo'lishi kerak!", reply_markup=get_admin_menu())


async def delete_product(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Faqat adminlar mahsulot o'chira oladi!", reply_markup=get_user_menu())
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Iltimos, mahsulot ID sini kiriting!", reply_markup=get_admin_menu())
        return

    try:
        product_id = int(args[1])
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id = ?", (product_id,))

        if c.rowcount > 0:
            await message.answer(f"Mahsulot (ID: {product_id}) o'chirildi!", reply_markup=get_admin_menu())
        else:
            await message.answer("Bunday ID li mahsulot topilmadi!", reply_markup=get_admin_menu())

        conn.commit()
        conn.close()
    except ValueError:
        await message.answer("Mahsulot ID raqam bo'lishi kerak!", reply_markup=get_admin_menu())


async def update_product(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Faqat adminlar mahsulot o'zgartira oladi!", reply_markup=get_user_menu())
        return

    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.answer("Iltimos, mahsulot ID, nomi, kategoriya ID va narxini kiriting!",
                             reply_markup=get_admin_menu())
        return

    try:
        product_id = int(args[1])
        name = args[2]
        category_id = int(args[3])
        price = float(args[4])

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE products SET name = ?, category_id = ?, price = ? WHERE id = ?",
                  (name, category_id, price, product_id))

        if c.rowcount > 0:
            await message.answer(f"Mahsulot (ID: {product_id}) o'zgartirildi!", reply_markup=get_admin_menu())
        else:
            await message.answer("Bunday ID li mahsulot topilmadi!", reply_markup=get_admin_menu())

        conn.commit()
        conn.close()
    except ValueError:
        await message.answer("ID, kategoriya ID va narx raqam bo'lishi kerak!", reply_markup=get_admin_menu())


async def list_products(message: types.Message):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT p.id, p.name, c.name, p.price FROM products p JOIN categories c ON p.category_id = c.id")
    products = c.fetchall()
    conn.close()

    if not products:
        await message.answer("Mahsulotlar topilmadi!",
                             reply_markup=get_admin_menu() if is_admin(message.from_user.id) else get_user_menu())
        return

    response = "Mahsulotlar ro'yxati:\n"
    for product in products:
        response += f"ID: {product[0]}, Nomi: {product[1]}, Kategoriya: {product[2]}, Narx: {product[3]}\n"
    await message.answer(response, reply_markup=get_admin_menu() if is_admin(message.from_user.id) else get_user_menu())


async def search(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Iltimos, qidirish uchun so'z kiriting!",
                             reply_markup=get_admin_menu() if is_admin(message.from_user.id) else get_user_menu())
        return

    search_term = args[1]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT p.id, p.name, c.name, p.price FROM products p JOIN categories c ON p.category_id = c.id WHERE p.name LIKE ?",
        (f'%{search_term}%',))
    products = c.fetchall()
    conn.close()

    if not products:
        await message.answer("Hech narsa topilmadi!",
                             reply_markup=get_admin_menu() if is_admin(message.from_user.id) else get_user_menu())
        return

    response = "Qidiruv natijalari:\n"
    for product in products:
        response += f"ID: {product[0]}, Nomi: {product[1]}, Kategoriya: {product[2]}, Narx: {product[3]}\n"
    await message.answer(response, reply_markup=get_admin_menu() if is_admin(message.from_user.id) else get_user_menu())
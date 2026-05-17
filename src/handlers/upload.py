from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config import SETTINGS
from src.keyboards.file_pagination import YandexDiskPagination
from src.services.yandex_disk_service import YandexDiskServices

router = Router()
service = YandexDiskServices(SETTINGS["YADISK_TOKEN"])
pagination = YandexDiskPagination(service, per_page=5)

# FSM состояния
class UploadStates(StatesGroup):
    waiting_for_folder = State()  # ожидание выбора папки
    file_data = State()           # сохранённые данные файла

@router.message(F.document)
async def upload_handler(message: Message, state: FSMContext):
    """Пользователь отправил файл - сохраняем его и показываем выбор папки"""
    try:
        # Получаем информацию о файле
        document = message.document
        file_name = document.file_name
        file_id = document.file_id
        
        # Скачиваем файл из Telegram
        file = await message.bot.get_file(file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        # Сохраняем данные файла в FSM
        await state.update_data(
            file_bytes=file_bytes.read(),
            file_name=file_name,
            file_id=file_id
        )
        await state.set_state(UploadStates.waiting_for_folder)
        
        # Показываем выбор папки
        page = 0
        text = pagination.get_page_text(page)
        keyboard = pagination.get_keyboard(page)
        
        await message.answer(
            f"📄 **Файл `{file_name}` получен!**\n\n"
            f"Теперь выберите папку на Яндекс.Диске для загрузки:\n\n{text}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении файла: {str(e)}")

@router.callback_query(lambda c: c.data.startswith('nav:'))
async def handle_navigation(callback: types.CallbackQuery, state: FSMContext):
    """Навигация по страницам папок"""
    _, new_page_str = callback.data.split(':')
    new_page = int(new_page_str)
    
    text = pagination.get_page_text(new_page)
    keyboard = pagination.get_keyboard(new_page)
    
    await callback.message.edit_text(
        f"📁 **Выберите папку для загрузки файла:**\n\n{text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith('select:'))
async def handle_select(callback: types.CallbackQuery, state: FSMContext):
    """Выбрана папка - загружаем в неё сохранённый файл"""
    _, idx_str = callback.data.split(':')
    idx = int(idx_str)
    
    try:
        # Получаем путь к выбранной папке
        path = pagination.get_item_path_by_index(idx)
        name = pagination._load_items()[idx][0]
        
        # Получаем сохранённые данные файла из FSM
        user_data = await state.get_data()
        file_bytes = user_data.get('file_bytes')
        file_name = user_data.get('file_name')
        
        if not file_bytes or not file_name:
            await callback.answer(
                "❌ Файл не найден. Пожалуйста, отправьте файл заново.", 
                show_alert=True
            )
            await state.clear()
            return
        
        # Отправляем уведомление о начале загрузки
        await callback.message.edit_text(
            f"⏳ **Загрузка файла `{file_name}`**\n"
            f"📁 В папку: `{name}`\n\n"
            f"Пожалуйста, подождите...",
            parse_mode="Markdown"
        )
        
        # Формируем полный путь на Яндекс.Диске
        target_path = f"{path}/{file_name}"
        
        # Загружаем файл на Яндекс.Диск
        service.upload_file(file_bytes, target_path)
        
        # Успех
        await callback.message.edit_text(
            f"✅ **Файл успешно загружен!**\n\n"
            f"📄 Имя: `{file_name}`\n"
            f"📁 Папка: `{name}`\n"
            f"🔗 Путь: `{target_path}`\n\n"
            f"📂 Чтобы загрузить другой файл - просто отправьте его мне.",
            parse_mode="Markdown"
        )
        
        # Очищаем состояние
        await state.clear()
        
    except IndexError:
        await callback.answer("❌ Ошибка: папка не найдена", show_alert=True)
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Ошибка загрузки:** {str(e)}\n\n"
            f"Попробуйте ещё раз, отправив файл заново.",
            parse_mode="Markdown"
        )
        await state.clear()
    
    await callback.answer()

# Дополнительно: обработка отмены
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена загрузки"""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("❌ Загрузка отменена. Отправьте новый файл, чтобы начать заново.")
    else:
        await message.answer("Нет активной загрузки для отмены.")
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class YandexDiskPagination:
    def __init__(self, service, per_page: int = 5):
        self.service = service
        self.per_page = per_page

    def _load_items(self):
        """Загружает список корневых папок"""
        return self.service.list_root_dirs()  # [(имя, путь), ...]

    def get_total_pages(self) -> int:
        items = self._load_items()
        return (len(items) + self.per_page - 1) // self.per_page

    def get_page_text(self, page: int) -> str:
        items = self._load_items()
        start = page * self.per_page
        end = start + self.per_page
        page_items = items[start:end]
        text = f"📄 Страница {page + 1}\n\n"
        text += "\n".join([name for name, _ in page_items])
        return text

    def get_keyboard(self, page: int):
        items = self._load_items()
        total_pages = self.get_total_pages()
        start = page * self.per_page
        end = start + self.per_page
        page_items = items[start:end]

        builder = InlineKeyboardBuilder()

        # Кнопки элементов с callback_data, содержащим индекс
        for idx, (name, _) in enumerate(page_items, start=start):
            builder.button(text=name, callback_data=f"select:{idx}")

        builder.adjust(1)  # каждая кнопка элемента на новой строке

        # Кнопки навигации (короткие callback_data)
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"nav:{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"nav:{page+1}"))

        if nav_buttons:
            builder.row(*nav_buttons)  # обе кнопки в одной строке

        return builder.as_markup()

    def get_item_path_by_index(self, index: int) -> str:
        """Возвращает путь к папке по индексу"""
        items = self._load_items()
        if 0 <= index < len(items):
            return items[index][1]
        raise IndexError("Индекс вне диапазона")
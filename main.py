import os
import logging
from typing import List, Dict, Any
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния пользователей (для кнопки "Назад")
user_states = {}

class BotMenus:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню"""
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="🧮 Решить пример", callback_data="solve_math"),
            InlineKeyboardButton(text="📚 Примеры задач", callback_data="show_examples"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def back_button(target: str = "main_menu") -> InlineKeyboardMarkup:
        """Универсальная кнопка Назад"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=target))
        return builder.as_markup()

    @staticmethod
    def examples_menu() -> InlineKeyboardMarkup:
        """Меню с примерами задач"""
        builder = InlineKeyboardBuilder()
        examples = [
            ("2 + 2 * 2", "example_2+2*2"),
            ("x**2 - 4", "example_x^2-4"),
            ("diff(x**2, x)", "example_diff"),
            ("integrate(x, x)", "example_integrate"),
            ("solve(x**2 - 4, x)", "example_solve")
        ]
        
        for text, callback in examples:
            builder.add(InlineKeyboardButton(text=text, callback_data=callback))
        
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

class MathSolver:
    @staticmethod
    def solve_expression(expression: str) -> Dict[str, Any]:
        """
        Решает математическое выражение и возвращает пошаговое решение
        """
        try:
            # Инициализация символов
            x, y, z = symbols('x y z')
            
            # Парсинг выражения
            expr = parse_expr(expression, transformations='all')
            
            steps = []
            result = None
            
            # Определяем тип выражения и решаем соответствующим образом
            if expression.startswith('solve'):
                # Решение уравнений
                equation = expr
                steps.append(f"**Уравнение:** `{equation}`")
                steps.append("**Шаг 1:** Приводим уравнение к стандартному виду")
                solutions = solve(equation, x)
                steps.append(f"**Шаг 2:** Находим корни уравнения")
                result = f"Решения: {solutions}"
                
            elif expression.startswith('diff'):
                # Дифференцирование
                func = expr
                steps.append(f"**Функция:** `{func}`")
                steps.append("**Шаг 1:** Находим производную")
                derivative = diff(func, x)
                steps.append(f"**Шаг 2:** Упрощаем результат")
                result = f"Производная: `{derivative}`"
                
            elif expression.startswith('integrate'):
                # Интегрирование
                func = expr
                steps.append(f"**Функция:** `{func}`")
                steps.append("**Шаг 1:** Находим интеграл")
                integral = integrate(func, x)
                steps.append(f"**Шаг 2:** Добавляем константу интегрирования")
                result = f"Интеграл: `{integral} + C`"
                
            else:
                # Обычные математические выражения
                steps.append(f"**Выражение:** `{expression}`")
                steps.append("**Шаг 1:** Вычисляем значение")
                simplified = simplify(expr)
                steps.append(f"**Шаг 2:** Упрощаем результат")
                result = f"Результат: `{simplified}`"
            
            return {
                "success": True,
                "steps": steps,
                "result": result,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "steps": [],
                "result": None,
                "error": f"Ошибка: {str(e)}"
            }

# ========== ОБРАБОТЧИКИ КОМАНД ==========

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 **Добро пожаловать в Math Solver Bot!**

Я могу решать математические задачи любой сложности:
• 📊 Арифметические выражения
• 🧮 Алгебраические уравнения  
• 📈 Дифференциальное исчисление
• ∫ Интегралы
• И многое другое!

Просто напишите математическое выражение, и я решу его поэтапно!
    """
    
    await message.answer(
        welcome_text,
        reply_markup=BotMenus.main_menu(),
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📖 **Справка по использованию бота**

**Поддерживаемые операции:**
• Базовые: `+`, `-`, `*`, `/`, `**` 
• Функции: `sin(x)`, `cos(x)`, `log(x)`
• Решение уравнений: `solve(x**2 - 4, x)`
• Дифференцирование: `diff(x**2, x)`
• Интегрирование: `integrate(x, x)`

**Примеры:**
• `(2 + 3) * 5`
• `x**2 + 2*x + 1`
• `solve(x**2 - 9, x)`
• `diff(sin(x), x)`

Просто введите выражение - я его решу!
    """
    
    await message.answer(
        help_text,
        reply_markup=BotMenus.back_button(),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТЧИКИ CALLBACK-КНОПОК ==========

@dp.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    welcome_text = """
🤖 **Главное меню Math Solver Bot**

Выберите действие или просто введите математическое выражение!
    """
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=BotMenus.main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "solve_math")
async def solve_math_callback(callback: types.CallbackQuery):
    """Кнопка решения математики"""
    text = """
🧮 **Режим решения математических выражений**

Просто введите любое математическое выражение в чат!

**Примеры:**
• `2 + 2 * 2`
• `x**2 - 4`
• `solve(x**2 - 9, x)`
• `diff(sin(x), x)`
    """
    
    await callback.message.edit_text(
        text,
        reply_markup=BotMenus.back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "show_examples")
async def show_examples_callback(callback: types.CallbackQuery):
    """Показать примеры задач"""
    text = """
📚 **Примеры математических выражений**

Выберите пример для автоматической вставки, или введите свой:
    """
    
    await callback.message.edit_text(
        text,
        reply_markup=BotMenus.examples_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    """Кнопка помощи"""
    await cmd_help(callback.message)
    await callback.answer()

# Обработчики примеров
@dp.callback_query(F.data.startswith("example_"))
async def example_callback(callback: types.CallbackQuery):
    """Обработка выбора примера"""
    examples_map = {
        "example_2+2*2": "2 + 2 * 2",
        "example_x^2-4": "x**2 - 4", 
        "example_diff": "diff(x**2, x)",
        "example_integrate": "integrate(x, x)",
        "example_solve": "solve(x**2 - 4, x)"
    }
    
    expression = examples_map.get(callback.data)
    if expression:
        # Имитируем отправку сообщения с этим выражением
        await process_math_expression(callback.message, expression, is_example=True)
    
    await callback.answer()

# ========== ОБРАБОТЧИК ЛЮБЫХ СООБЩЕНИЙ ==========

@dp.message(F.text)
async def process_math_expression(message: types.Message, expression: str = None, is_example: bool = False):
    """Обработчик ЛЮБЫХ текстовых сообщений"""
    user_text = expression or message.text
    
    # Игнорируем команды
    if user_text.startswith('/'):
        return
    
    # Показываем "печатает..."
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Решаем математическое выражение
    solution = MathSolver.solve_expression(user_text)
    
    # Формируем ответ
    if solution["success"]:
        response = f"🧮 **Решение выражения:** `{user_text}`\n\n"
        
        # Добавляем шаги решения
        for step in solution["steps"]:
            response += f"• {step}\n"
        
        response += f"\n✅ **{solution['result']}**"
        
    else:
        response = f"❌ **Не удалось решить выражение:** `{user_text}`\n\n"
        response += f"**Ошибка:** {solution['error']}\n\n"
        response += "Проверьте правильность ввода и попробуйте снова."
    
    # Отправляем ответ с кнопкой "Назад"
    await message.answer(
        response,
        reply_markup=BotMenus.back_button("solve_math"),
        parse_mode="Markdown"
    )

# ========== VERCEL WEBHOOK SETUP ==========

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    webhook_url = os.getenv('VERCEL_URL') + '/api/webhook'
    await bot.set_webhook(webhook_url)
    logger.info(f"Bot started with webhook: {webhook_url}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    await bot.session.close()
    logger.info("Bot stopped")

# Vercel требует функцию для обработки запросов
async def webhook_handler(request):
    """Обработчик вебхука для Vercel"""
    url = str(request.url)
    index = url.rfind('/')
    token = url[index+1:]
    
    if token != BOT_TOKEN:
        return web.Response(status=403)
    
    update = types.Update(**(await request.json()))
    await dp.feed_webhook_update(bot, update)
    
    return web.Response(status=200, text="OK")

# Локальный запуск для тестирования
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

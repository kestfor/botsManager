# bot/handlers.py
from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from bot.config import load_config
from bot.controller import ServiceController
from bot.utils import parse_docker_ps

router = Router()
config = load_config(config_path="../config.json")
controller = ServiceController(config['services'])


# Callback data factory
class ServiceCB(CallbackData, prefix="svc"):
    service: str
    action: str  # menu, start, stop, restart, back


# Helper to build main menu keyboard
def build_main_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for svc in controller.list_services():
        buttons.append([
            InlineKeyboardButton(
                text=svc,
                callback_data=ServiceCB(service=svc, action="menu").pack()
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Helper to build service actions keyboard
def build_service_keyboard(svc: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Start",
                callback_data=ServiceCB(service=svc, action="start").pack()
            ),
            InlineKeyboardButton(
                text="Stop",
                callback_data=ServiceCB(service=svc, action="stop").pack()
            ),
            InlineKeyboardButton(
                text="Restart",
                callback_data=ServiceCB(service=svc, action="restart").pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="Back",
                callback_data=ServiceCB(service=svc, action="back").pack()
            )
        ]
    ])


# /start command: show main menu
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = build_main_keyboard()
    await message.answer("Select a service:", reply_markup=keyboard)


# Callback handler for all service actions
@router.callback_query(ServiceCB.filter())
async def service_menu(callback: types.CallbackQuery, callback_data: ServiceCB):
    svc = callback_data.service
    act = callback_data.action

    if act == "menu":
        raw = controller.status(svc)
        pretty = parse_docker_ps(raw)
        await callback.message.edit_text(
            f"📦 Статус сервиса <b>{svc}</b>:\n{pretty}",
            parse_mode=ParseMode.HTML,
            reply_markup=build_service_keyboard(svc)
        )

    elif act in ("start", "stop", "restart"):
        try:
            if act == "start":
                output = controller.start(svc)
            elif act == "stop":
                output = controller.stop(svc)
            else:
                output = controller.restart(svc)

            raw = controller.status(svc)
            pretty = parse_docker_ps(raw)
            await callback.message.edit_text(
                (
                    f"Action <b>{act}</b> executed for <b>{svc}</b>:\n\n"
                    f"📦 Текущий статус:\n{pretty}"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=build_service_keyboard(svc)
            )
        except Exception as e:
            await callback.message.edit_text(
                str(e),
                parse_mode=ParseMode.HTML,
                reply_markup=build_main_keyboard()
            )
            await callback.answer()
            return

    elif act == "back":
        await callback.message.edit_text(
            "Select a service:",
            reply_markup=build_main_keyboard()
        )

    await callback.answer()


# Fallback text commands
def parse_command_arg(message: types.Message) -> str | None:
    parts = message.text.strip().split()
    return parts[1] if len(parts) > 1 else None


@router.message(Command("status"))
async def cmd_status_text(message: types.Message):
    name = parse_command_arg(message)
    if not name:
        return await message.reply("Usage: /status <service>")
    raw = controller.status(name)
    pretty = parse_docker_ps(raw)
    await message.answer(
        f"📦 Статус <b>{name}</b>:\n{pretty}",
        parse_mode=ParseMode.HTML
    )


@router.message(Command("start"))
async def cmd_start_text(message: types.Message):
    name = parse_command_arg(message)
    if not name:
        return await message.reply("Usage: /start <service>")
    output = controller.start(name)
    await message.answer(
        f"✅ <b>{name}</b> запущен.\n{output}",
        parse_mode=ParseMode.HTML
    )


@router.message(Command("stop"))
async def cmd_stop_text(message: types.Message):
    name = parse_command_arg(message)
    if not name:
        return await message.reply("Usage: /stop <service>")
    output = controller.stop(name)
    await message.answer(
        f"❌ <b>{name}</b> остановлен.\n{output}",
        parse_mode=ParseMode.HTML
    )


@router.message(Command("restart"))
async def cmd_restart_text(message: types.Message):
    name = parse_command_arg(message)
    if not name:
        return await message.reply("Usage: /restart <service>")
    output = controller.restart(name)
    await message.answer(
        f"🔄 <b>{name}</b> перезапущен.\n{output}",
        parse_mode=ParseMode.HTML
    )

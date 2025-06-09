from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import Member
import os

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Acesso negado. Você não é um administrador.")
        return
    
    keyboard = [
        [InlineKeyboardButton("Listar Membros", callback_data='list_members')],
        [InlineKeyboardButton("Editar Membro", callback_data='edit_member')],
        [InlineKeyboardButton("Alterar Status", callback_data='toggle_status')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Painel de Administração:', reply_markup=reply_markup)

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'list_members':
        await list_members(update, context)
    elif query.data == 'edit_member':
        await query.edit_message_text(text="Digite o ID do membro que deseja editar:")
        context.user_data['admin_action'] = 'edit_member'
    elif query.data == 'toggle_status':
        await query.edit_message_text(text="Digite o ID do membro para alterar o status:")
        context.user_data['admin_action'] = 'toggle_status'

async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = Member.select()
    response = "Lista de Membros:\n\n"
    
    for member in members:
        response += f"ID: {member.id}\nNome: {member.name}\nFunção: {member.function}\nStatus: {member.status}\n\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def is_admin(user_id: int) -> bool:
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    return user_id in admin_ids

def setup_admin_handlers(application):
    application.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^(list_members|edit_member|toggle_status)$'))
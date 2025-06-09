import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from dotenv import load_dotenv
from database import Member, initialize_db
from card_generator import CardGenerator
from admin import admin_panel, setup_admin_handlers
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

NAME, ADDRESS, BIRTH_DATE, FUNCTION, CONFIRMATION = range(5)
card_generator = CardGenerator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        member = Member.get(Member.user_id == user.id)
        await update.message.reply_text(
            f"Olá {member.name}! Você já está registrado.\n"
            "Use /card para ver sua carteirinha ou /update para atualizar seus dados."
        )
        return ConversationHandler.END
    except Member.DoesNotExist:
        pass
    
    await update.message.reply_text(
        "Olá! Vamos criar sua carteirinha virtual.\n"
        "Por favor, digite seu nome completo:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Ótimo! Agora digite seu endereço completo:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Agora digite sua data de nascimento (DD/MM/AAAA):")
    return BIRTH_DATE

async def get_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birth_date'] = update.message.text
    await update.message.reply_text("Qual é a sua função/cargo?")
    return FUNCTION

async def get_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['function'] = update.message.text
    
    user_data = context.user_data
    confirmation_message = (
        "Por favor, confira seus dados:\n\n"
        f"Nome: {user_data['name']}\n"
        f"Endereço: {user_data['address']}\n"
        f"Data de Nascimento: {user_data['birth_date']}\n"
        f"Função: {user_data['function']}\n\n"
        "Está tudo correto? (Sim/Não)"
    )
    
    await update.message.reply_text(confirmation_message)
    return CONFIRMATION

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.lower()
    
    if response == 'sim':
        user = update.effective_user
        user_data = context.user_data
        
        Member.create(
            user_id=user.id,
            chat_id=update.effective_chat.id,
            name=user_data['name'],
            address=user_data['address'],
            birth_date=user_data['birth_date'],
            function=user_data['function'],
            status='Ativo'
        )
        
        await update.message.reply_text("Cadastro concluído com sucesso!")
        await send_card(update, context)
        return ConversationHandler.END
    elif response == 'não':
        await update.message.reply_text("Vamos começar novamente. Digite seu nome completo:")
        return NAME
    else:
        await update.message.reply_text("Por favor, responda com 'Sim' ou 'Não'.")
        return CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operação cancelada.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        member = Member.get(Member.user_id == user.id)
        member_data = {
            'user_id': member.user_id,
            'name': member.name,
            'address': member.address,
            'birth_date': member.birth_date,
            'function': member.function,
            'status': member.status
        }
        
        card_path = card_generator.generate_card(member_data)
        
        with open(card_path, 'rb') as card_file:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=card_file,
                caption=f"Sua carteirinha virtual - Status: {member.status}"
            )
        
        os.remove(card_path)
        
    except Member.DoesNotExist:
        await update.message.reply_text("Você ainda não está registrado. Use /start para se cadastrar.")

async def update_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        member = Member.get(Member.user_id == user.id)
        context.user_data['member_id'] = member.id
        
        await update.message.reply_text(
            "Vamos atualizar seus dados. Qual informação deseja alterar?\n\n"
            "1. Nome\n2. Endereço\n3. Data de Nascimento\n4. Função\n\n"
            "Digite o número correspondente:"
        )
        
        return 'UPDATE_FIELD'
    except Member.DoesNotExist:
        await update.message.reply_text("Você ainda não está registrado. Use /start para se cadastrar.")
        return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Comandos disponíveis:\n\n"
        "/start - Iniciar cadastro\n"
        "/card - Visualizar sua carteirinha\n"
        "/update - Atualizar seus dados\n"
        "/help - Mostrar esta mensagem"
    )
    
    if is_admin(update.effective_user.id):
        help_text += "\n\nComandos de administrador:\n/admin - Painel de administração"
    
    await update.message.reply_text(help_text)

def is_admin(user_id: int) -> bool:
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    return user_id in admin_ids

def main():
    load_dotenv()
    initialize_db()
    
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birth_date)],
            FUNCTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_function)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('card', send_card))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('update', update_info))
    application.add_handler(CommandHandler('admin', admin_panel))
    setup_admin_handlers(application)
    
    application.run_polling()

if __name__ == '__main__':
    main()
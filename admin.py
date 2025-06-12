from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import Member
import os

# Estados da conversa
WAITING_MEMBER_ID = 1
WAITING_EDIT_DATA = 2

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
        context.user_data['conversation_state'] = WAITING_MEMBER_ID
    elif query.data == 'toggle_status':
        await query.edit_message_text(text="Digite o ID do membro para alterar o status:")
        context.user_data['admin_action'] = 'toggle_status'
        context.user_data['conversation_state'] = WAITING_MEMBER_ID

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'conversation_state' not in context.user_data:
        return
    
    user_input = update.message.text
    state = context.user_data['conversation_state']
    action = context.user_data['admin_action']

    if state == WAITING_MEMBER_ID:
        try:
            member_id = int(user_input)
            member = Member.get_or_none(Member.id == member_id)
            
            if not member:
                await update.message.reply_text("❌ Membro não encontrado! Digite um ID válido.")
                return
            
            context.user_data['current_member_id'] = member_id
            
            if action == 'edit_member':
                await update.message.reply_text(
                    f"Editando membro ID {member_id}:\n\n"
                    f"Nome atual: {member.name}\n"
                    f"Função atual: {member.function}\n\n"
                    "Envie os novos dados no formato:\n"
                    "<nome>|<função>\n\n"
                    "Exemplo: João Silva|Desenvolvedor"
                )
                context.user_data['conversation_state'] = WAITING_EDIT_DATA
                
            elif action == 'toggle_status':
                new_status = not member.status
                Member.update(status=new_status).where(Member.id == member_id).execute()
                status_text = "ativo" if new_status else "inativo"
                await update.message.reply_text(f"✅ Status do membro ID {member_id} alterado para {status_text}!")
                del context.user_data['conversation_state']
                
        except ValueError:
            await update.message.reply_text("❌ ID inválido! Digite apenas números.")
    
    elif state == WAITING_EDIT_DATA and action == 'edit_member':
        try:
            name, function = user_input.split('|')
            member_id = context.user_data['current_member_id']
            
            Member.update(name=name.strip(), function=function.strip()).where(Member.id == member_id).execute()
            
            await update.message.reply_text(f"✅ Membro ID {member_id} atualizado com sucesso!")
            del context.user_data['conversation_state']
            
        except Exception as e:
            await update.message.reply_text("❌ Formato inválido! Use: <nome>|<função>")

async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = Member.select()
    response = "Lista de Membros:\n\n"
    
    for member in members:
        status = "✅ Ativo" if member.status else "❌ Inativo"
        response += f"ID: {member.id}\nNome: {member.name}\nFunção: {member.function}\nStatus: {status}\n\n"
    
    if isinstance(update, Update):
        chat_id = update.effective_chat.id
    else:  # Se for chamado de CallbackQuery
        chat_id = update.message.chat_id
    
    await context.bot.send_message(chat_id=chat_id, text=response)

def is_admin(user_id: int) -> bool:
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    return user_id in admin_ids

def setup_admin_handlers(application):
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^(list_members|edit_member|toggle_status)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))

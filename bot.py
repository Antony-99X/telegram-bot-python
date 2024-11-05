from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import os

# Bot Token from environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Star Prices
STAR_PRICES = {
    13: 32.5,
    26: 65,
    43: 107.5,
    85: 212.5,
    450: 1125,
    825: 2062.5
}

# Payment Details
PAYMENT_DETAILS = {
    "Binance": "YOUR_BINANCE_ID",
    "bKash": "YOUR_BKASH_NUMBER",
    "Nagad": "YOUR_NAGAD_NUMBER"
}

# Start command
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Buy Star ⭐", callback_data='buy_star')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome! Please click 'Buy Star ⭐' to place an order.", reply_markup=reply_markup)

# Buy Star Callback
def buy_star(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # Star Quantity Options
    keyboard = [[InlineKeyboardButton(f"{amount} Stars", callback_data=f'star_{amount}')] for amount in STAR_PRICES.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="How many stars would you like to buy?", reply_markup=reply_markup)

# Handle Star Selection
def star_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    quantity = int(query.data.split('_')[1])
    price = STAR_PRICES[quantity]
    query.answer()
    # Payment Method Options
    keyboard = [
        [InlineKeyboardButton("Binance", callback_data=f'pay_Binance_{quantity}'),
         InlineKeyboardButton("bKash", callback_data=f'pay_bKash_{quantity}'),
         InlineKeyboardButton("Nagad", callback_data=f'pay_Nagad_{quantity}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"{quantity} Stars cost {price} BDT.\nChoose your payment method:", reply_markup=reply_markup)

# Payment Method Selection
def payment_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    _, method, quantity = query.data.split('_')
    quantity = int(quantity)
    payment_info = PAYMENT_DETAILS[method]
    query.answer()
    query.edit_message_text(
        text=f"Please send {STAR_PRICES[quantity]} BDT via {method} to: {payment_info}\nThen upload a payment screenshot here."
    )
    context.user_data['order'] = {
        'quantity': quantity,
        'method': method,
        'status': 'pending'
    }

# Handle Payment Screenshot
def handle_screenshot(update: Update, context: CallbackContext):
    if 'order' in context.user_data and context.user_data['order']['status'] == 'pending':
        order = context.user_data['order']
        order['status'] = 'submitted'
        order['screenshot'] = update.message.photo[-1].file_id
        update.message.reply_text("Thank you! Your order is now pending. We will confirm soon.")
        # Notify admin here, e.g., save to database or send notification

# Main function to setup handlers and start bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(buy_star, pattern='^buy_star$'))
    dp.add_handler(CallbackQueryHandler(star_selection, pattern='^star_'))
    dp.add_handler(CallbackQueryHandler(payment_selection, pattern='^pay_'))
    dp.add_handler(MessageHandler(Filters.photo, handle_screenshot))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

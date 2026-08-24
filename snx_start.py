import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from pya3 import *  # Ensure required functions are available
# from Non_indices_2 import nonIndicesFunction  # Blocking function
from snx_orders import final_orders_main

BOT_TOKEN = "8224871767:AAHsmEWHPOcFd24JoViESEJ4gGr_39aisOQ"

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle messages asynchronously
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    # Run nonIndicesFunction in the background without waiting
    asyncio.create_task(process_message(update, user_message,access_token))

# Function to process messages in a separate async task
async def process_message(update: Update, user_message: str,access_token) -> None:
    try:
        # Run the function in a separate thread so it doesn't block
        response = await asyncio.to_thread(final_orders_main, access_token,user_message)  
        await update.message.reply_text(response if response else "No response generated.")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot is running! Send a message to process.")

def main(access_token):
    # Initialize bot application
    app = Application.builder().token(BOT_TOKEN).build()
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Run bot in polling mode
    logger.info("Bot is starting...")
    app.run_polling()
import csv

def read_access_tokens(csv_file_path):
    access_tokens = []

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            token = row.get('access_token')
            if token:  # avoid empty values
                access_tokens.append(token)

    return access_tokens


# Example usage

# print(tokens)
if __name__ == "__main__":
    access_token = read_access_tokens('access_token.csv')
    # access_token = ['eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0S0I3WTciLCJqdGkiOiI2OTdlYzlhMjBhODU1ZTRkODJiMTAxZDIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2OTkxNjgzNCwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY5OTgzMjAwfQ.3_jeXTfLF9hPpw5hTxJG0_EJnXc4ZeMvAmUqWGOEBP8'
                    
    # ]
    
    main(access_token)
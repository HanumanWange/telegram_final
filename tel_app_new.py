import logging
from telegram import Update
from telegram.ext import ContextTypes,Application, MessageHandler, filters, CommandHandler, CallbackContext
# from your_program import process_message  # ✅ Import the function directly
# from pya3 import *
import asyncio
from wrapper import *
from application_new import main_nifty
# Replace with your Telegram Bot Token
BOT_TOKEN = "5875551957:AAHKOIgfbLk00C5MNjforJA4iLKKsLIgLoI"
# BOT_TOKEN = '8048320138:AAEfGtYQEPAQxrNl9_99mQ-zVn2JqeQ9e0I'


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_message(update: Update, user_message: str,alice) -> None:
    try:
        # Run the function in a separate thread so it doesn't block
        response = await asyncio.to_thread(main_nifty, alice,user_message)  
        await update.message.reply_text(response if response else "No response generated.")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("An error occurred while processing your request.")


# Function to handle messages asynchronously
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    
    # Run nonIndicesFunction in the background without waiting
    asyncio.create_task(process_message(update, user_message,alice))



# Function to execute when a message is received
# async def handle_message(update: Update, context: CallbackContext) -> None:
#     user_message = update.message.text
#     response = main_nifty(alice,user_message)  # ✅ Pass the message to the function
#     await update.message.reply_text(response)
    
#     # if user_message == 'a':
#     #     response = main_nifty(alice,user_message)  # ✅ Pass the message to the function
#     #     await update.message.reply_text(response)  # ✅ Send the processed output back
#     # elif user_message == '':
#     #     response = process_message(user_message)  # ✅ Pass the message to the function
#     #     await update.message.reply_text(response)  # ✅ Send the processed output back

    

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Bot is running! Send a message to process.")

def main(alice):
    # Initialize bot application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot in polling mode
    app.run_polling()

if __name__ == "__main__":

    # user_id_assgn = '2498200'
    # api_key_assgn = 'tQ2RXG1QHIjDfabMVKrmiBiaa9V5MAl2DYA3qXbBPfB10xUuUt7hgu3gSRUySyMhd9kESpQkoaXq2YhnRcnFny84K2SpEQqgv5psmFsuT9XN1kTeayLUhCqcxHyOqhWf'

    user_id_assgn = '545150'
    api_key_assgn = 'KmhnQpPBZyCpjfcydTo8PtELkQB3q0ahukecNIZcXrEE25WzStae2oklIHFol25qx72m3eo9tu5d5s5UrySIM0sRiKDINIkFsc4GBQy5MVlu8panGZfJtJ3afq4WuzJj'




    # user_id_assgn = '1680737'
    # api_key_assgn ='S2jVBuakTjbkkmusbubKGoAhqBKRCpzvXmRNx9ekh9Vxal9nHpPWVRFNvSrNhzTQzPka6QHThU6qcXaEaj2zhyvXHnQAa7YCXYlcVqc0v319hOysal3DGSRCOfVWrCQc'
    global alice
    alice = 'a'
    alice = Aliceblue(user_id=user_id_assgn,api_key=api_key_assgn)
    alice.get_session_id()
    alice.get_contract_master("NFO")

    main(alice)

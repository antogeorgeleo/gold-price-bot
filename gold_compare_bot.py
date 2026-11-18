from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from reportlab.pdfgen import canvas
from datetime import datetime

TOKEN = "9020509245:AAGZDp-XIENjbqTL8cMhTG40DCg_vjQyVAY"

INDIA_PRICE = 1
VN_PRICE = 2

user_data_store = {}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Gold Price Comparison Bot\n\n"
        "Enter Indian Gold Price (₹ per gram):"
    )
    return INDIA_PRICE

# Get India Price
async def india_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        user_data_store[update.effective_chat.id] = {"india": price}

        await update.message.reply_text(
            "Enter Vietnam Gold Price (VND per chi):"
        )
        return VN_PRICE

    except:
        await update.message.reply_text("Enter valid number.")
        return INDIA_PRICE

# Get Vietnam Price
async def vn_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        vn_chi = float(update.message.text)

        chat_id = update.effective_chat.id

        india_price = user_data_store[chat_id]["india"]

        # 1 chi = 3.75 gram
        vn_gram = vn_chi / 3.75

        india_pavan = india_price * 8
        vn_pavan = vn_gram * 8

        pdf_file = f"Gold_Comparison_{chat_id}.pdf"

        c = canvas.Canvas(pdf_file)

        c.setFont("Helvetica-Bold", 18)
        c.drawString(100, 800, "Gold Price Comparison")

        c.setFont("Helvetica", 12)

        c.drawString(50, 740,
                     f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

        c.drawString(50, 700,
                     f"India Gold Price : ₹ {india_price:.2f} / gram")

        c.drawString(50, 670,
                     f"Vietnam Gold Price : {vn_chi:,.0f} VND / chi")

        c.drawString(50, 640,
                     f"Vietnam Gold Price : {vn_gram:,.0f} VND / gram")

        c.drawString(50, 600,
                     f"India Price Per Pavan (8g): ₹ {india_pavan:.2f}")

        c.drawString(50, 570,
                     f"Vietnam Price Per Pavan (8g): {vn_pavan:,.0f} VND")

        c.save()

        with open(pdf_file, "rb") as pdf:
            await update.message.reply_document(
                document=pdf,
                filename=pdf_file
            )

        await update.message.reply_text(
            "PDF comparison report generated successfully."
        )

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)}"
        )
        return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

def main():

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INDIA_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               india_price)
            ],
            VN_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               vn_price)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Gold Comparison Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
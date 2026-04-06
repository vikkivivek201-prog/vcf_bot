import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8728597335:AAGiUAbgh4BEBT7FPkR7aTJhlAYwTcHQn2o"
ADMIN_ID = 5328734113

main_menu = [
    ["📁 Text to VCF", "📄 VCF to Text"],
    ["🔄 Merge VCF", "📦 Split Text"],  # ✅ New button added
    ["⚓ Admin/Navy", "💎 Buy Premium"],
]

user_state = {}
vcf_files = {}

# LOAD USERS
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        with open("users.json", "w") as f:
            f.write("{}")
        return {}

# SAVE USERS
def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.message.from_user.id)

    if uid not in users:
        users[uid] = {"premium": False}
        save_users(users)

    await update.message.reply_text(
        "🔥 ULTRA PRO BOT 🔥",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)  # <-- menu => main_menu
    )

# HANDLE DOCUMENT
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = await update.message.document.get_file()
    filename = update.message.document.file_name

    if not filename.endswith(".txt"):
        await update.message.reply_text("❌ Please send a TXT file only.")
        return

    # Save the TXT file
    path = f"{user_id}.txt"
    await file.download_to_drive(path)

    # Initialize state
    user_state[user_id] = {
        "step": "name",
        "file": path
    }

    await update.message.reply_text("❖ Enter Contact Name ❖")

# ---------------- HANDLE TEXT ----------------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = await update.message.document.get_file()
    filename = update.message.document.file_name

    if not filename.endswith(".txt"):
        await update.message.reply_text("❌ Please send a TXT file only.")
        return

    # Save the TXT file
    path = f"{user_id}.txt"
    await file.download_to_drive(path)

    # Initialize state
    user_state[user_id] = {
        "step": "name",
        "file": path
    }

    await update.message.reply_text("Step 1️⃣ - Enter Contact Name:")

# ---------------- HANDLE TEXT ----------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state = user_state.get(user_id)

    # Button press: Text to VCF
    if text == "📁 Text to VCF":
        await update.message.reply_text("Send your TXT file to start converting into VCF")
        return

    if not state:
        await update.message.reply_text("❌ Please send a TXT file first.")
        return

    # Step 1: Contact Name
    if state["step"] == "name":
        state["name"] = text
        state["step"] = "prefix"
        await update.message.reply_text("Step 2️⃣ - Enter VCF File Prefix/Name:")
        return

    # Step 2: VCF Prefix
    if state["step"] == "prefix":
        state["prefix"] = text
        state["step"] = "limit"
        await update.message.reply_text("Step 3️⃣ - Enter Contacts per VCF (example: 50):")
        return

    # Step 3: Contacts per VCF
    if state["step"] == "limit":
        try:
            limit = int(text)
        except ValueError:
            await update.message.reply_text("❌ Enter a valid number for contacts per VCF.")
            return

        state["limit"] = limit

        # Read TXT file
        with open(state["file"], encoding="utf-8") as f:
            numbers = f.read().splitlines()

        # Split into chunks based on limit
        chunks = [numbers[i:i+limit] for i in range(0, len(numbers), limit)]

        for idx, chunk in enumerate(chunks):
            vcf_content = ""
            for i, num in enumerate(chunk):
                vcf_content += "BEGIN:VCARD\n"
                vcf_content += "VERSION:3.0\n"
                vcf_content += f"FN:{state['prefix']} {state['name']} {i+1}\n"
                vcf_content += f"TEL;TYPE=CELL:{num}\n"
                vcf_content += "END:VCARD\n"

            vcf_filename = f"{state['prefix']}_{idx+1}.vcf"
            with open(vcf_filename, "w", encoding="utf-8") as f:
                f.write(vcf_content)

            await update.message.reply_document(open(vcf_filename, "rb"))
            os.remove(vcf_filename)

        await update.message.reply_text("✅ Text to VCF Done!")
        user_state.pop(user_id, None)

    # MENU
    if text == "📦 Split TXT":
        if not users[uid]["premium"]:
            await update.message.reply_text("❌ Premium only feature")
            return
    user_state[user_id] = {"step": "split_txt"}
    await update.message.reply_text("Send TXT file to split into multiple smaller TXT files")
    return

    if not users[uid]["premium"]:
        await update.message.reply_text("❌ Premium only feature")
        return
    user_state[user_id] = {"step": "split_txt"}
    await update.message.reply_text("Send TXT file to split into multiple smaller TXT files")
    return
    s
    if text == "💎 Buy Premium":
        await update.message.reply_text("Contact admin to buy premium")
        return
    

# ADMIN COMMAND
async def add_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        uid = context.args[0]
        users = load_users()

        if uid not in users:
            users[uid] = {"premium": True}
        else:
            users[uid]["premium"] = True

        save_users(users)
        await update.message.reply_text("User upgraded to premium ✅")

    except:
        await update.message.reply_text("Error ❌")

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addpremium", add_premium))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.TEXT, handle_text))

print("🔥 ULTRA PRO RUNNING 🔥")
app.run_polling()
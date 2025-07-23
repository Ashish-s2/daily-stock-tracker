import os
import datetime
import yfinance as yf
import openai

# List of stocks to track
STOCKS = {
    "DIXON.NS": "Dixon Technologies",
    "RELIANCE.NS": "Reliance",
    "TCS.NS": "TCS",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank"
}

# Get today’s date
today = datetime.datetime.now().strftime('%Y-%m-%d')

# Make folders
os.makedirs("stocks", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# 1️⃣ Fetch stock prices & save
summary_lines = []

for symbol, name in STOCKS.items():
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    
    if data.empty:
        print(f"❌ No data for {name}")
        continue

    price = round(data['Close'][0], 2)
    file_path = f"stocks/{symbol.replace('.NS', '')}_{today}.txt"

    with open(file_path, "w") as f:
        f.write(f"{name} ({symbol}) closing price on {today}: ₹{price}")
    
    summary_lines.append(f"{name} closed at ₹{price}")

# 2️⃣ Generate OpenAI Summary
openai.api_key = os.environ.get("OPENAI_API_KEY")

prompt = (
    "Write a short and smart daily Indian stock market summary based on these prices:\n" +
    "\n".join(summary_lines) +
    "\nKeep it simple, catchy, and blog-style."
)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
)

summary = response['choices'][0]['message']['content']

# Save summary
summary_file = f"summaries/{today}.md"
with open(summary_file, "w", encoding="utf-8") as f:
    f.write(f"# Market Summary - {today}\n\n{summary}")

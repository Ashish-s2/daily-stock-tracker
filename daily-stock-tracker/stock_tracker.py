import os
import datetime
import openai
import yfinance as yf
import pandas as pd

# Stock symbols
symbols = ["DIXON.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "^NSEI"]
today = datetime.datetime.now().strftime("%Y-%m-%d")
stock_folder = f"stocks/{today}"
os.makedirs(stock_folder, exist_ok=True)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Track and save stock data individually
for symbol in symbols:
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d")
    if not hist.empty:
        price = hist["Close"].iloc[-1]
        df = pd.DataFrame([[today, symbol, round(price, 2)]], columns=["Date", "Symbol", "Price"])
        df.to_csv(f"{stock_folder}/{symbol.replace('^', '').replace('.', '')}.csv", index=False)
        os.system(f'git add {stock_folder}/{symbol.replace("^", "").replace(".", "")}.csv')
        os.system(f'git commit -m "📈 Added price for {symbol} on {today}"')

# Optional: Generate OpenAI summary
summary = f"Today is {today}. Here is a summary of the tracked stocks:\n"
for symbol in symbols:
    summary += f"- {symbol}\n"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful financial analyst."},
        {"role": "user", "content": f"Write a short stock market summary for these symbols: {', '.join(symbols)} for {today}."}
    ]
)
ai_text = response["choices"][0]["message"]["content"]
summary += "\n" + ai_text

# Save summary
summary_path = f"summaries/{today}.md"
with open(summary_path, "w") as f:
    f.write(summary)

os.system(f"git add {summary_path}")
os.system(f'git commit -m "🧠 Added AI stock summary for {today}"')

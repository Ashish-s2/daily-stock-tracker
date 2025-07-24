import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables!")

# Set API key for OpenAI
openai.api_key = OPENAI_API_KEY

# Define cryptocurrency tickers (from Yahoo Finance)
tickers = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD"]

# Today's date
today = datetime.now().strftime("%Y-%m-%d")

# Create output folders
os.makedirs("stock", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# To store all summaries
all_summaries = []

# Process each cryptocurrency
for ticker in tickers:
    print(f"📥 Downloading data for {ticker}...")
    data = yf.download(ticker, period="1d", interval="1h", auto_adjust=True)

    if data.empty:
        print(f"⚠️ No data for {ticker}")
        continue

    # Save data to CSV
    csv_file = f"stock/{ticker}_{today}.csv"
    data.to_csv(csv_file)
    print(f"✅ Saved: {csv_file}")

    # Create summary prompt
    prompt = (
        f"Analyze the hourly price data of {ticker} on {today} and provide a short financial summary.\n\n"
        f"Recent data:\n{data.tail().to_string()}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional crypto analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        summary = response.choices[0].message["content"].strip()
        print(f"🧠 Summary for {ticker}:\n{summary[:120]}...")
        all_summaries.append(f"## {ticker}\n{summary}\n")

    except Exception as e:
        print(f"❌ Error with OpenAI for {ticker}: {e}")

# Save all summaries to a markdown file
if all_summaries:
    summary_file = f"summaries/{today}.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Daily Crypto Summary – {today}\n\n")
        f.write("\n".join(all_summaries))
    print(f"✅ Summary saved to: {summary_file}")
else:
    print("⚠️ No summaries generated.")

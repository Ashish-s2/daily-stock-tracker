import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai

# Load environment variables from .env file (for local use)
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables!")

# Set the API key for OpenAI
openai.api_key = OPENAI_API_KEY

# Define stock tickers
tickers = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

# Today's date string
today = datetime.now().strftime("%Y-%m-%d")

# Create output directories
os.makedirs("stock", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# Summary accumulator
all_summaries = []

# Fetch and process each stock
for ticker in tickers:
    print(f"📈 Fetching data for {ticker}...")
    data = yf.download(ticker, period="1d", interval="1h", auto_adjust=True)
    if data.empty:
        print(f"⚠️ No data available for {ticker}")
        continue

    # Save to CSV
    csv_filename = f"stock/{ticker}_{today}.csv"
    data.to_csv(csv_filename)
    print(f"✅ Saved: {csv_filename}")

    # Create prompt for OpenAI
    prompt = (
        f"Analyze the intraday stock data of {ticker} on {today} and provide a financial summary.\n\n"
        f"Recent data snapshot:\n{data.tail().to_string()}"
    )

    # Generate summary using OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        summary = response.choices[0].message["content"].strip()
        print(f"🧠 Summary for {ticker}:\n{summary[:100]}...")
        all_summaries.append(f"### {ticker}\n{summary}\n")

    except Exception as e:
        print(f"❌ Error generating summary for {ticker}: {e}")
        continue

# Save all summaries to markdown
if all_summaries:
    summary_path = f"summaries/{today}.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Daily Stock Summary\n\n")
        f.write("\n".join(all_summaries))
    print(f"✅ Summary saved: {summary_path}")
else:
    print("⚠️ No summaries generated.")

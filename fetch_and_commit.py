import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# List of stock tickers
tickers = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

# Today's date
today = datetime.now().strftime("%Y-%m-%d")

# Create folders if not exist
os.makedirs("stock", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

all_summaries = []

for ticker in tickers:
    # Download today's stock data
    data = yf.download(ticker, period="1d", interval="1h")
    if data.empty:
        print(f"No data for {ticker}")
        continue

    # Save CSV
    csv_path = f"stock/{ticker}_{today}.csv"
    data.to_csv(csv_path)

    # Prepare prompt
    prompt = (
        f"Analyze the intraday stock data of {ticker} on {today} and give a summary.\n\n"
        f"Here is the data:\n{data.tail().to_string()}"
    )

    # Generate summary using OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    summary = response.choices[0].message.content.strip()
    all_summaries.append(f"### {ticker}\n{summary}\n")

# Save markdown summary
if all_summaries:
    summary_path = f"summaries/{today}.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Daily Stock Summary\n\n")
        f.write("\n".join(all_summaries))

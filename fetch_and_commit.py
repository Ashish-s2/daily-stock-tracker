import yfinance as yf
import os
from datetime import datetime
import openai

STOCKS = {
    'DIXON.NS': 'Dixon Technologies',
    'RELIANCE.NS': 'Reliance',
    'TCS.NS': 'TCS',
    'HDFCBANK.NS': 'HDFC Bank',
    'INFY.NS': 'Infosys'
}

def fetch_stock_data(ticker):
    data = yf.download(ticker, period="1d", interval="1d")
    if data.empty:
        return None
    row = data.iloc[0]
    return {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Open": round(row['Open'], 2),
        "High": round(row['High'], 2),
        "Low": round(row['Low'], 2),
        "Close": round(row['Close'], 2),
        "Volume": int(row['Volume'])
    }

def save_to_csv(ticker, data):
    folder = "stock"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{ticker.replace('.NS', '')}.csv")
    header = "Date,Open,High,Low,Close,Volume\n"
    line = f"{data['Date']},{data['Open']},{data['High']},{data['Low']},{data['Close']},{data['Volume']}\n"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(header)
    with open(filename, "a") as f:
        f.write(line)

def generate_summary(all_data):
    summary_lines = [f"📊 **Stock Summary for {datetime.now().strftime('%Y-%m-%d')}**\n"]
    for stock, info in all_data.items():
        summary_lines.append(f"- **{STOCKS[stock]}** closed at ₹{info['Close']} (Open: ₹{info['Open']})")
    prompt = "\n".join(summary_lines) + "\n\nWrite a short daily summary of this market performance:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_summary(text):
    os.makedirs("summaries", exist_ok=True)
    fname = datetime.now().strftime("summaries/%Y-%m-%d.md")
    with open(fname, "w") as f:
        f.write(text)

def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    all_data = {}
    for ticker in STOCKS:
        data = fetch_stock_data(ticker)
        if data:
            save_to_csv(ticker, data)
            all_data[ticker] = data
    summary = generate_summary(all_data)
    save_summary(summary)

if __name__ == "__main__":
    main()

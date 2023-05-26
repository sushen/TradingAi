symbol = "BTCBUSD"

data = {
    'Sum': -1700,
    'Non-zero indicators': "1m_CDLBELTHOLD(-100), 1m_CDLCLOSINGMARUBOZU(-100), 1m_CDLLONGLINE(-100), "
                           "1m_CDLMARUBOZU(-100), 1m_CDLSEPARATINGLINES(-100), 1m_bollinger_band(100), "
                           "3m_CDLBELTHOLD(-100.0), 3m_CDLCLOSINGMARUBOZU(-100.0), 3m_CDLLONGLINE(-100.0), "
                           "3m_CDLMARUBOZU(-100.0), 3m_CDLSEPARATINGLINES(-100.0), 5m_CDLBELTHOLD(-100.0), "
                           "5m_CDLCLOSINGMARUBOZU(-100.0), 5m_CDLLONGLINE(-100.0), 5m_CDLMARUBOZU(-100.0), "
                           "15m_CDLBELTHOLD(-100.0), 15m_CDLCLOSINGMARUBOZU(-100.0), 15m_CDLLONGLINE(-100.0), "
                           "15m_CDLMARUBOZU(-100.0)"
}

# Format the data
subject = f"\033[1m{symbol} Bullish\033[0m"
body_lines = [
    subject,
    '-' * len(subject),
    "",
    f"Bullish Signal for {symbol} Symbol",
    "",
    f"Total Signal Value: {data['Sum']}",
    "",
    "Details:",
    f"- Sum: {data['Sum']}",
    "- Non-zero indicators:"
]
body_lines.extend(f"    {line}" for line in data['Non-zero indicators'].split(", "))
body = "\n".join(body_lines)

# Print the formatted text
print(body)

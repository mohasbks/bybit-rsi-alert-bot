<div align="center">
  <h1>🤖 Cryptocurrency Trading Bot with RSI Indicator</h1>
  <p>
    <strong>Smart RSI monitoring for USDT Perpetual markets on Bybit</strong>
  </p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

## Key Features

- 🚀 **Instant Alerts** for RSI above 85
- ⚡ **Cooldown Override** for RSI above 90
- 📊 **Periodic Reports** every 30 minutes
- 🛡️ **Cooldown Protection** (4 hours)
- 🔄 **Automatic Scanning** every minute (configurable)
- 📝 **Detailed Logs** of all operations

## 🛠 Requirements

- Python 3.8 or newer
- Bybit account (for API access)
- Telegram Bot Token (get from @BotFather)
- Telegram Chat ID (for receiving alerts)

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/bybit-rsi-bot.git
   cd bybit-rsi-bot
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Telegram Bot:**
   - Open @BotFather in Telegram
   - Create a new bot using `/newbot` command
   - Save the Bot Token provided by BotFather

5. **Configuration:**
   - Copy the example config file:
   ```bash
   cp config.example.json config.json
   ```
   - Edit `config.json` with your settings:
     - `telegram_token`: Your Telegram Bot Token
     - `telegram_chat_id`: Your Telegram Chat ID
     - Adjust other settings as needed

## ⚙️ Configuration

Customize the bot's behavior in `config.json`:

```json
{
    "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "check_interval_minutes": 1,
    "rsi_period": 14,
    "rsi_high_threshold": 85,
    "rsi_extreme_threshold": 90,
    "cooldown_hours": 4,
    "report_interval_minutes": 30,
    "timeframe": "4h",
    "max_retries": 3,
    "retry_delay_seconds": 5
}
```

### Configuration Options:

- `telegram_token`: Your Telegram Bot Token (required)
- `telegram_chat_id`: Target chat ID for alerts (required)
- `check_interval_minutes`: Market scan frequency in minutes (default: 1)
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_high_threshold`: Minimum RSI level for alerts (default: 85)
- `rsi_extreme_threshold`: RSI level that overrides cooldown (default: 90)
- `cooldown_hours`: Hours to wait before resending alerts for the same coin (default: 4)
- `report_interval_minutes`: Minutes between status reports (default: 30)
- `timeframe`: Candle timeframe (default: "4h")
- `max_retries`: Maximum retry attempts for failed requests (default: 3)
- `retry_delay_seconds`: Delay between retry attempts (default: 5)

## 🚀 Running the Bot

Start the bot with:

```bash
python perfect_rsi_bot.py
```

### What Happens When Running?

1. **Initialization**:
   - Load settings from `config.json`
   - Test Telegram bot connection
   - Fetch all USDT Perpetual trading pairs from Bybit

2. **Monitoring Cycle**:
   - Scan RSI for all pairs every minute
   - Send instant alerts when:
     - RSI reaches 85 or above (if cooldown has passed)
     - RSI reaches 90 or above (overrides cooldown)
   - Send periodic status reports
   - Log all operations

3. **Error Handling**:
   - Automatic retry for failed requests
   - Error logging and notifications
   - Automatic recovery after disconnections

### Additional Commands

To verify RSI calculations for a specific symbol:

```bash
python verify_rsi.py BTCUSDT
```

This will manually calculate RSI and compare it with the bot's values for verification.

## 📨 Message Examples

### 1. High RSI Alert (85+)
```
🚨 *High RSI Alert!*

📊 *Symbol:* `BTCUSDT`
📈 *RSI Level:* 87.5
🕒 *Time:* 2023-11-15 14:30:00
⚠️ *Note:* RSI above 85

📊 *Details:*
- Current Price: 37,542.50 USDT
- 24h Change: +3.2%
- 24h Volume: 1.2B USDT

🔔 *Next Alert:* In 4 hours (unless RSI crosses 90)
```

### 2. Extreme RSI Alert (90+)
```
🔥 *Warning! Extreme RSI!* 🔥

📊 *Symbol:* `ETHUSDT`
📈 *RSI Level:* 92.8
🕒 *Time:* 2023-11-15 14:35:00
⚠️ *Warning:* RSI above 90 - Cooldown overridden!

📊 *Details:*
- Current Price: 2,145.30 USDT
- 24h Change: +5.7%
- 24h Volume: 850M USDT

🔔 *Next Alert:* Will send another alert if RSI continues to rise
```

### 3. Periodic Market Report (Every 30 minutes)
```
📊 *Market Status Report*

🕒 Last Updated: 2023-11-15 14:30:00

📊 *RSI Statistics:*
🔴 RSI ≥ 90: 2 coins
🟠 RSI 85-89: 5 coins
🟡 RSI 70-84: 12 coins
🟢 RSI < 70: 533 coins

📈 *Top 5 Coins by RSI:*
1. `DOGEUSDT`: 93.2 📈
2. `XRPUSDT`: 91.8 📈
3. `SOLUSDT`: 88.3 ⬆️
4. `ADAUSDT`: 86.7 ⬆️
5. `MATICUSDT`: 82.1 ➡️

⏳ Next update in 30 minutes...
```

## 🐛 Troubleshooting

### Bot Not Sending Messages
- ✅ Verify `telegram_token` in `config.json`
- ✅ Ensure the bot is a member of the specified group
- ✅ Check bot permissions in the group (must be able to send messages)
- ✅ Check logs for any errors

### Bybit Connection Issues
- 🌐 Check your internet connection
- 🔄 Try changing DNS server to 8.8.8.8 or 1.1.1.1
- ⏱ Add delay between requests if hitting rate limits

### RSI Calculation Issues
- 📊 Use the verification tool to validate calculations:
  ```bash
  python verify_rsi.py BTCUSDT
  ```
- 🔄 Make sure all dependencies are up to date:
  ```bash
  pip install --upgrade pandas pandas_ta requests
  ```

## 📊 Logging and Monitoring

The bot logs all operations to the following files:
- `bot.log`: Detailed operation log
- `alerts.log`: Log of all sent alerts
- `errors.log`: Error and exception log

Monitor logs in real-time using:
```bash
tail -f bot.log  # Linux/Mac
Get-Content -Path "bot.log" -Wait  # Windows PowerShell
```

## 💡 Tips and Strategies

### Using the Bot Effectively

1. **Risk Management**
   - Use bot signals as part of a comprehensive trading strategy
   - Don't rely solely on RSI signals for trading decisions
   - Always use stop-loss orders

2. **Performance Optimization**
   - Reduce the number of monitored pairs for better performance
   - Use a VPS for continuous operation
   - Adjust scan intervals based on your needs

3. **Customization**
   - Experiment with different RSI periods (7, 14, 21)
   - Adjust alert thresholds based on market conditions
   - Try different candle timeframes (1h, 4h, 1d)

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the project (`git clone`)
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Stage your changes (`git add .`)
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### Features Wanted

- [ ] Add more technical indicators (MACD, Bollinger Bands)
- [ ] Support other exchanges (Binance, FTX, etc.)
- [ ] Web interface for bot control
- [ ] More customization options

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:
- 📧 Email: 235179@eru.edu.eg
- 📱 Telegram: [@helloworled](https://t.me/helloworled)

---
🙏 Acknowledgments
Bybit team for the amazing API

Developers of Python libraries used in this project

Open-source financial community

<div align="center"> <p>Made with ❤️ for crypto traders</p> <p>🚀 Happy Trading! 🚀</p> </div>
  <p>Made with ❤️ for crypto traders</p>
  <p>🚀 Happy Trading! 🚀</p>
</div>  to english

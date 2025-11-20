# EDEM SNOSER

A Telegram bot for anonymous email and SMS flooding, code spamming, and account disruption services. Built with aiogram and supports subscription-based access.

## Features

- **Email Flooder**: Send anonymous emails via SMTP or Mailgun
- **SMS Flooder**: Mass SMS sending (placeholder)
- **Code Spammer**: Spam Telegram verification codes to phone numbers
- **Account Disruption**: Tools for "snos" (account takedown) operations
- **Subscription System**: Paid access with CryptoBot and AAIO payment integration
- **Admin Panel**: Statistics, user management, and broadcasting

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `config.py` with your API keys and settings
4. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

Edit `config.py` with your credentials:

- `TOKEN`: Your Telegram bot token
- `admin_ids`: List of admin user IDs
- SMTP/Mailgun settings for email sending
- `CRYPTOPAY_TOKEN`: For cryptocurrency payments
- Database path

## Usage

### User Commands

- `/start`: Initialize the bot and show main menu
- `/buy`: Purchase subscription
- `/admin`: Admin panel (admin only)

### Features

1. **Email Flooder**: Send multiple emails to targets (subscription required)
2. **Code Spammer**: Spam verification codes to phone numbers (subscription required)
3. **SMS Flooder**: Placeholder for SMS functionality
4. **Support**: Contact support

### Admin Features

- View statistics (total users, subscribers, payments)
- Broadcast messages to all users
- Manage subscriptions manually

## Database

Uses SQLite database (`database.db`) with user management and subscription tracking.

## Payment Integration

- **CryptoBot**: USDT payments
- **AAIO**: Alternative payment processor

## Disclaimer

This tool is for educational purposes only. Use at your own risk. The developers are not responsible for any misuse or illegal activities.
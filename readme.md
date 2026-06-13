# 📱 Telegram Premium Bot - Complete Documentation

<div align="center">

![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-0088cc?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003b57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### 🚀 Feature-Rich Telegram Bot with Premium Membership System

[Features](#-features) • [Setup](#-setup--installation) • [Commands](#-commands) • [Configuration](#-configuration) • [Screenshots](#-screenshots)

</div>

---

## 📖 Overview

A complete Telegram bot solution with premium membership management, payment integration, broadcast system, and much more. Perfect for content creators, channel owners, and businesses looking to monetize their Telegram presence.

### ✨ Key Features

| Category | Features |
|----------|----------|
| **💎 Premium System** | Multi-plan subscriptions, Discount system (1-25% random), Secure invite links (10s expiry), Premium user panel |
| **🎨 Start System** | Customizable start message with HTML/Markdown, Custom start image support, Dynamic inline buttons |
| **💰 Payment Integration** | UPI payments, Auto payment URL generation, Payment verification workflow, Screenshot & UTR submission |
| **📢 Broadcast System** | Message with buttons support, Photo + caption broadcast, Send to all users, Delivery statistics |
| **👥 User Management** | Auto user backup (users.txt), Database rebuild from backup, User statistics, Premium status tracking |
| **🔧 Admin Controls** | ?? prefix for admin commands, Full configuration panel, Plan management, Button management |

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.9 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Server/VPS (Recommended) or local machine

### Step 1: Clone Repository

```bash
git clone https://github.com/x-lgr/pompombot.git
cd pompombot
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required: Your bot token from @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrsTUVwxyz

# Required: Admin user IDs (comma-separated, no spaces)
ADMIN_IDS=123456789,987654321

# Optional: Custom payment URL template
# Default template used if not specified
PAYMENT_URL_TEMPLATE=https://redirect-beta-lemon.vercel.app/{upiname}/{bankname}/{amount}
```

### Step 5: Run the Bot

```bash
python main.py
```

### Step 6: Setup Bot Commands (Optional)

Send these commands to [@BotFather](https://t.me/BotFather):

```
/setcommands
start - Start the bot
help - Show help menu
premium - Premium user panel
status - Check account status
```

---

## 📝 Commands

### 👤 User Commands (Single Slash `/`)

| Command | Description |
|---------|-------------|
| `/start` | Launch bot and show start message |
| `/help` | Display help menu with available commands |
| `/premium` | Access premium user panel (premium users only) |
| `/status` | Check your account status (free/premium) |

### 👑 Admin Commands (Double Question Mark `??`)

#### Start Message Management
| Command | Description |
|---------|-------------|
| `??setstart` | Set custom start message (supports HTML/placeholders) |
| `??viewstart` | View current start message |
| `??resetstart` | Restore default start message |

#### Start Image Management
| Command | Description |
|---------|-------------|
| `??setstartimage` | Set custom start image |
| `??viewstartimage` | Preview current start image |
| `??removestartimage` | Remove current start image |
| `??resetstartimage` | Restore default image |

#### Button Management
| Command | Description |
|---------|-------------|
| `??addbutton` | Add new button (asks name & URL) |
| `??removebutton` | Remove existing button |
| `??editbutton` | Edit button name or URL |
| `??buttons` | List all configured buttons |

#### Plan Management
| Command | Description |
|---------|-------------|
| `??addplan` | Create new premium plan |
| `??editplan` | Edit existing plan |
| `??removeplan` | Delete a plan |
| `??plans` | List all plans |

#### Payment Configuration
| Command | Description |
|---------|-------------|
| `??setupi` | Set UPI ID (e.g., example@upi) |
| `??setupiname` | Set UPI name for payment URL |
| `??setreceiver` | Set receiver name |
| `??setbankname` | Set bank name for payment URL |
| `??setpaymenturl` | Set custom payment URL template |

#### Channel Settings
| Command | Description |
|---------|-------------|
| `??setpremiumchannel` | Set premium channel (bot must be admin) |
| `??setdemochannel` | Set demo channel URL |

#### Broadcast & Users
| Command | Description |
|---------|-------------|
| `??broadcast` | Send broadcast message to all users |
| `??backupusers` | Download users.txt backup file |
| `??importusers` | Import users from uploaded file |
| `??rebuilddb` | Rebuild database from users.txt |

#### Status & Statistics
| Command | Description |
|---------|-------------|
| `??status` | Show bot system status |
| `??stats` | Show advanced statistics |
| `??payments` | Review pending payments |
| `??help` | Show all admin commands |

---

## ⚙️ Configuration Guide

### 1. Setting Up Start Message

```bash
??setstart
```
Then send your message. Supports:
- HTML formatting: `<b>Bold</b>`, `<i>Italic</i>`
- Placeholders: `{first_name}`, `{last_name}`, `{username}`, `{user_id}`

Example:
```
Welcome {first_name}! 👋
Your ID: {user_id}
<b>Enjoy premium content!</b>
```

### 2. Adding Start Buttons

```bash
??addbutton
```
Follow prompts to add:
- Button name (e.g., "Join Channel")
- Button URL (e.g., "https://t.me/mychannel")

### 3. Creating Premium Plans

```bash
??addplan
```
Provide:
- Plan name (e.g., "🔥 Premium Pro")
- Price in rupees (e.g., 199)
- Description (e.g., "Access all features")
- Duration (e.g., "30 days" or "Lifetime")
- Sort order (1 = first position)

### 4. Configuring Payment System

```bash
# Set UPI details
??setupi
example@okhdfcbank

??setupiname
merchantname

??setreceiver
John Doe

??setbankname
bankname
```

The payment URL will be generated as:
`https://redirect-beta-lemon.vercel.app/merchantname/bankname/amount`

### 5. Setting Up Premium Channel

1. Add bot as admin to your premium channel
2. Get channel ID:
   - Forward a message from channel to @userinfobot
   - Or use: `-100` + channel ID
3. Set it:
```bash
??setpremiumchannel
-1001234567890
```

### 6. Demo Channel Configuration

```bash
??setdemochannel
https://t.me/demochannel
```

---

## 🗄️ Database Structure

### Tables

| Table | Purpose |
|-------|---------|
| `users` | Store user information and premium status |
| `start_settings` | Custom start message and image |
| `start_buttons` | Start menu inline buttons |
| `plans` | Premium subscription plans |
| `discounts` | Generated discount codes |
| `pending_payments` | Payment verification queue |
| `payment_settings` | UPI and payment configuration |
| `channel_settings` | Premium and demo channels |

### Backup System

The bot maintains `users.txt` with one user ID per line:
```
123456789
987654321
555555555
```

To restore from backup:
```bash
??importusers  # Upload users.txt
??rebuilddb    # Rebuild database
```

---

## 🎯 Usage Examples

### User Flow

1. **User starts bot** → Sees welcome message with buttons
2. **Clicks "Buy Premium"** → Sees available plans
3. **Selects a plan** → Views plan details
4. **Clicks "Buy Now"** → Gets payment instructions
5. **Cancels payment** → Gets discount offer
6. **Makes payment** → Submits screenshot & UTR
7. **Admin approves** → User gets premium access
8. **Premium user** → Generates invite link to premium channel

### Admin Workflow

1. **Setup bot** → Configure start message, image, buttons
2. **Create plans** → Add pricing plans
3. **Configure payment** → Set UPI details
4. **Set channels** → Premium & demo channel config
5. **Review payments** → Approve/reject user submissions
6. **Send broadcasts** → Announcements to all users
7. **Manage users** → Backup, import, view statistics

---

## 🔒 Security Features

- **Admin-only commands** with `??` prefix
- **Secure invite links** (10-second expiry, one-time use)
- **User authentication** for premium access
- **Database protection** with automatic backups
- **Input validation** for URLs and user data
- **Error handling** throughout the bot

---

## 📁 Project Structure

```
telegram-premium-bot/
├── main.py                 # Entry point
├── config.py              # Configuration
├── database.py            # Database operations
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── users.txt              # User backup file
├── premium_bot.db         # SQLite database
├── handlers/
│   ├── user_handlers.py   # User commands
│   ├── admin_handlers.py  # Admin commands
│   ├── premium_handlers.py # Premium features
│   └── broadcast_handlers.py # Broadcast system
├── keyboards/
│   └── inline_keyboards.py # Button layouts
└── utils/
    ├── decorators.py      # Admin/auth decorators
    ├── helpers.py         # Utility functions
    └── user_backup.py     # Backup management
```

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Bot not responding | Check bot token in `.env` |
| Admin commands not working | Verify user ID in `ADMIN_IDS` |
| Payment URL not generating | Set `setupiname` and `setbankname` |
| Invite link fails | Ensure bot is admin in premium channel |
| Users not saving | Check `users.txt` file permissions |
| Broadcast fails | Verify bot can message users |

### Logs

Check console output for detailed error messages:
```
2024-01-01 12:00:00 - INFO - Bot started!
2024-01-01 12:00:05 - ERROR - Failed to send message to user
```

---

## 🔄 Deployment

### Using systemd (Linux)

Create service file:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Add:
```ini
[Unit]
Description=Telegram Premium Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/telegram-premium-bot
ExecStart=/home/youruser/telegram-premium-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

### Using screen

```bash
screen -S telegram-bot
python main.py
# Press Ctrl+A, then D to detach
# screen -r telegram-bot to reattach
```

---

## 📊 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ Yes | None | Bot token from @BotFather |
| `ADMIN_IDS` | ✅ Yes | None | Comma-separated admin user IDs |
| `PAYMENT_URL_TEMPLATE` | ❌ No | vercel.app link | Custom payment URL template |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see below:

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

Full license text available at: https://opensource.org/licenses/MIT
```

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/x-lgr/pompombot/issues)
- **Telegram**: [Support Channel](https://t.me/xlgr_158)


---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

<div align="center">

Made with ❤️ by [xlgr]

[Report Bug](https://github.com/yourusername/telegram-premium-bot/issues) • [Request Feature](https://github.com/yourusername/telegram-premium-bot/issues)

</div>

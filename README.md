# 🤖 Culi-Bot

A Telegram bot powered by **Grok AI** for intelligent Kubernetes alert analysis with playbook integration.

## 📋 Overview

**Culi-Bot** is a sophisticated Telegram chatbot designed to analyze Kubernetes alerts and provide AI-powered insights using Grok (x.ai). It integrates custom playbooks for domain-specific knowledge and maintains a SQLite database for alert deduplication and history tracking.

**Key Features:**
- 🧠 **AI-Powered Analysis**: Uses Grok AI (grok-3) to analyze and contextualize Kubernetes alerts
- 📖 **Playbook Support**: Match alerts to internal playbooks for tailored responses
- 🔄 **Alert Deduplication**: Prevents spam by tracking recent alerts with configurable cooldown
- 📊 **Database Persistence**: SQLite-based alert history and analytics
- 🐳 **Docker Ready**: Pre-configured Docker and docker-compose setup
- ⚙️ **Admin Commands**: Status, statistics, and playbook management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Grok API Key (from [x.ai](https://x.ai))
- Docker & Docker Compose (optional)

### Installation

#### Option 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShadowHunter1/culi-bot.git
   cd culi-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_token_here
   GROK_API_KEY=your_grok_api_key_here
   BOT_USERNAME=your_bot_username  # e.g., culi_bot (without @)
   GROK_MODEL=grok-3               # Default: grok-3
   DATABASE_PATH=data/culi_bot.db  # Default: data/culi_bot.db
   PLAYBOOKS_DIR=playbooks         # Default: playbooks
   ```

4. **Run the bot**
   ```bash
   python -m bot.main
   ```

#### Option 2: Docker (Recommended)

```bash
docker-compose up -d
```

The docker-compose setup includes:
- Persistent SQLite database volume (`./data`)
- Playbook hot-reload support (`./playbooks`)
- JSON logging with rotation (10MB max, 3 files retention)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python-telegram-bot` | 21.6 | Telegram Bot API wrapper |
| `httpx` | 0.27.0 | Async HTTP client for Grok API |
| `python-dotenv` | 1.0.1 | Environment variable management |

---

## 📁 Project Structure

```
culi-bot/
├── bot/
│   ├── main.py              # Application entry point
│   ├── handlers.py          # Message and alert handler logic
│   ├── admin.py             # Admin commands (/status, /stats, etc.)
│   ├── database.py          # SQLite database operations
│   ├── grok_client.py       # Grok AI API integration
│   ├── parser.py            # Alert message parsing
│   └── playbook_loader.py   # Playbook file loading & matching
├── playbooks/               # Custom Kubernetes playbooks (YAML/Markdown)
├── data/                    # Persistent data (SQLite DB, created at runtime)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # This file
```

---

## 🎮 Bot Commands

### User Commands

**Analyze an Alert**
```
@culi_bot
alert: PodCrashLooping
namespace: production
severity: critical
```
The bot will:
1. Parse the alert message
2. Check for recent similar alerts (deduplication)
3. Find a matching playbook
4. Send to Grok AI for analysis
5. Reply with formatted insights

### Admin Commands

| Command | Description |
|---------|-------------|
| `/status` | Check bot uptime and health |
| `/stats` | View alert statistics (total alerts, unique alerts) |
| `/recent` | Show recently analyzed alerts |
| `/reload_playbooks` | Reload playbooks without restarting |

---

## 📖 Playbook System

Playbooks are Markdown files organized by category that provide context-specific knowledge.

### Playbook Structure

**File**: `playbooks/kubernetes/pod_crashes.md`
```markdown
# Pod Crash Handling

## Common Causes
- OOM Killer
- Liveness probe failures
- Resource limits

## Resolution Steps
1. Check pod logs
2. Verify resource allocation
3. Review probe configuration
```

### Playbook Matching

The bot matches alerts to playbooks using alert names:
- Alert: `PodCrashLooping` → searches `playbooks/` for matching files
- If found, playbook content is sent to Grok alongside the alert
- If not found, Grok uses Kubernetes general knowledge

### Hot-Reload

Update playbook files in the `./playbooks/` directory and run:
```
/reload_playbooks
```

No need to restart the container!

---

## 🧠 AI Analysis Flow

```
User Alert
    ↓
Alert Parser (extract: name, namespace, severity)
    ↓
Deduplication Check (prevent spam within 30 min cooldown)
    ↓
Playbook Lookup (find matching playbook)
    ↓
Grok API Call (with system prompt + playbook context)
    ↓
Database Save (for history & stats)
    ↓
Formatted Response to Telegram
```

### System Prompt

The bot uses `playbooks/AI_PROMPT_SPEC.md` as the system prompt for Grok. Customize this file to shape AI behavior:

```markdown
# AI System Prompt

You are a Kubernetes expert assistant analyzing production alerts.
- Provide concise, actionable insights
- Reference the playbook when available
- Focus on quick resolution steps
```

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Telegram Bot API token |
| `GROK_API_KEY` | ✅ | - | x.ai Grok API key |
| `BOT_USERNAME` | ✅ | - | Bot username (for @mention detection) |
| `GROK_MODEL` | ❌ | `grok-3` | Grok model version |
| `DATABASE_PATH` | ❌ | `data/culi_bot.db` | SQLite database path |
| `PLAYBOOKS_DIR` | ❌ | `playbooks` | Playbooks directory |

---

## 💾 Database Schema

The bot maintains a SQLite database with alert history:

| Table | Purpose |
|-------|---------|
| `alerts` | Stores alert analysis history |
| `dedup_cache` | Tracks recent alerts for deduplication |

### Sample Queries

**Get recent alerts:**
```sql
SELECT alertname, namespace, severity, analyzed_at 
FROM alerts 
ORDER BY analyzed_at DESC 
LIMIT 10;
```

**Get alert count by severity:**
```sql
SELECT severity, COUNT(*) as count 
FROM alerts 
GROUP BY severity;
```

---

## 🐛 Troubleshooting

### Bot doesn't respond to messages

- **Check 1**: Verify bot is mentioned: `@culi_bot` in message
- **Check 2**: Confirm message contains valid alert format
- **Check 3**: Review logs: `docker-compose logs -f culi-bot`

### Grok API errors

- **Check**: Verify `GROK_API_KEY` is correct
- **Solution**: Use `docker-compose restart culi-bot` after fixing

### Alert deduplication too aggressive

- **Adjust**: Modify `dedup_cooldown` in `bot/handlers.py` (default: 1800 seconds = 30 minutes)

### Playbooks not loading

- **Check**: Files exist in `./playbooks/` directory
- **Solution**: Run `/reload_playbooks` command or restart container

---

## 📚 Tech Stack

- **Framework**: `python-telegram-bot` (Telegram Bot API)
- **AI**: Grok (x.ai) via `httpx` async client
- **Database**: SQLite
- **Container**: Docker + Docker Compose
- **Python**: 3.12 (slim image)

---

## 🔄 Deployment

### Local Development
```bash
python -m bot.main
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f
```

### Production Considerations

- Use environment secrets (not `.env` files)
- Enable database backups: mount `/app/data` to persistent storage
- Monitor logs: configure external log aggregation
- Set up alert routing: group Kubernetes alerts before sending to bot

---

## 📝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source. See LICENSE file for details.

---

## 🤝 Support

For issues, questions, or feature requests, please open a GitHub issue.

---

## 🌟 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Powered by [Grok AI](https://x.ai) (xAI)
- Designed for Kubernetes on-call teams

---

**Made with ❤️ by ShadowHunter1**

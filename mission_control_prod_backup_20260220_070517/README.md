# 🚀 Mission Control Dashboard

Personal command center for Rai — portfolio, schedule, ideas, and system status.

## 🎯 Features

- **📈 Portfolio Tracker** — Real-time holdings, gains/losses, alerts
- **📅 Earnings Calendar** — Upcoming earnings dates  
- **📍 Schedule** — Your events + son's activities (today/tomorrow highlighted)
- **💡 Ideas & Notes** — Searchable repository of your thoughts
- **🛒 Grocery List** — Current shopping items
- **⚙️ System Status** — Health of all automated systems

## 🚀 Quick Start

### Option 1: Run Directly
```bash
cd /Users/raitsai/.openclaw/workspace/mission_control
python3 server.py
```
Open: **http://localhost:5000**

### Option 2: Use Start Script
```bash
cd /Users/raitsai/.openclaw/workspace/mission_control
./start.sh
```

## 📱 Access

### From Mac (Local)
- Open browser to `http://localhost:5000`

### From Phone/iPad (Same WiFi)
1. Find your Mac's IP: `System Settings > Network`
2. Open: `http://[MAC_IP]:5000` on phone

Example: `http://192.168.1.100:5000`

## 🔄 Auto-Refresh

Dashboard refreshes every **5 minutes** automatically.

Manual refresh: Click the **Refresh** button on any card.

## 🔍 Search Ideas

Type in the search box under "Ideas & Notes" to filter your stored thoughts.

## 🎨 Design

- **Dark mode** — Easy on the eyes
- **Mobile responsive** — Works on phone/tablet
- **Color coded** — Green gains, red losses, yellow alerts

## 📁 Data Sources

Dashboard reads from your workspace files:
- `portfolio/portfolio_tracker.md`
- `son_schedule.md`
- `ideas/NOTES.md`
- `grocery_list.md`

Changes to these files appear on next refresh.

## 🛠️ Troubleshooting

**Port 5000 in use?**
```bash
lsof -ti:5000 | xargs kill -9  # Kill existing process
```

**Can't access from phone?**
- Make sure phone and Mac are on same WiFi
- Check firewall: `System Settings > Network > Firewall`
- Try Mac's IP instead of localhost

**Changes not showing?**
- Click Refresh button
- Or wait 5 minutes for auto-refresh

## 📝 Future Enhancements

- [ ] Real-time stock prices via API
- [ ] Calendar integration
- [ ] Push notifications
- [ ] Task/action item tracking
- [ ] Historical performance charts

---
Built with Flask + vanilla JS. No build step required.

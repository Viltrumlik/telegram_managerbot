# Deployment (VPS, systemd, 24/7)

Target: the `viltrumlik` folder on the server (assumed `/root/viltrumlik`).

## 1. Upload code
From the local project root:
```bash
rsync -av --exclude venv --exclude __pycache__ --exclude subscribers.json \
  ./ root@<SERVER_IP>:/root/viltrumlik/
```

## 2. Python venv + deps
```bash
ssh root@<SERVER_IP>
cd /root/viltrumlik
apt update && apt install -y python3 python3-venv python3-pip
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

## 3. Secrets
Ensure `/root/viltrumlik/.env` exists with `BOT_TOKEN=...`, then lock it down:
```bash
chmod 600 /root/viltrumlik/.env
```

## 4. systemd service
```bash
cp /root/viltrumlik/deploy/managerbot.service /etc/systemd/system/managerbot.service
systemctl daemon-reload
systemctl enable --now managerbot
systemctl status managerbot --no-pager
journalctl -u managerbot -f      # follow logs; look for "Bot @<username> ishga tushdi"
```

## 5. Enable inline mode (one-time, in Telegram)
DM **@BotFather** → `/setinline` → choose the bot → set placeholder e.g. `100 usd uzs`.
Without this, inline conversion silently receives no updates.

## 6. Activate
Open the bot in Telegram and send `/start` (registers your chat for scheduled pushes).

## Operations
- Restart:  `systemctl restart managerbot`
- Logs:     `journalctl -u managerbot -e`
- Update:   re-run step 1 (rsync) then `systemctl restart managerbot`

## Security follow-up (do right after deploy)
- Add SSH key auth; disable password login (`PasswordAuthentication no` in `sshd_config`).
- Rotate the root password (it was shared in plaintext during setup).
- Optional: `ufw allow OpenSSH && ufw enable`.

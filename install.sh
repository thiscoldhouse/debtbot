mkdir -p /usr/src/venv
virtualenv --python $(which python3) /usr/src/venv/directactionbot

cat > /etc/systemd/system/directactionbot.service <<EOM
[Unit]
Description=Direct Action Bot
After=network.target

[Service]
Type=simple
User=tad
WorkingDirectory=/usr/src/directactionbot
ExecStart=/usr/src/venv/directactionbot/bin/python /usr/src/directactionbot/main.py
StandardOutput=syslog
StandardError=syslog
Restart=always

[Install]
WantedBy=multi-user.target
EOM

systemctl enable /etc/systemd/system/directactionbot.service

"""
cat /etc/systemd/system/hello.service

--

[Unit]
Description=hello
After= \
    syslog.target \
    network.target \
    remote-fs.target \
    nss-lookup.target \
    network-online.target
Requires=network-online.target

[Service]
Type=simple
StandardOutput=journal
ExecStart=sleep infinity

# User=
# WorkingDirectory=

# https://serverfault.com/questions/617823/how-to-set-systemd-service-dependencies
# PIDFile=/run/nginx.pid
# ExecStartPre=/usr/sbin/nginx -t
# ExecStart=/usr/sbin/nginx
# ExecReload=/bin/kill -s HUP $MAINPID
# ExecStop=/bin/kill -s QUIT $MAINPID
# PrivateTmp=true

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

--

sudo systemctl enable hello.service
sudo systemctl start hello.service

"""

# GlucoseSaver
git clone https://github.com/JanHalik/GlucoseSaver.git
# Pulls actual Glucose data from LibreLinkUp application.
On Ubuntu 24
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install --no-input -r requirements.txt
python PollingGlukose.py

# Run as service
# /etc/systemd/system/glucose.service
[Unit]
Description=My Python Service
After=network.target

[Service]
Type=simple
ExecStart=/home/ubuntu/git/GlucoseSaver/.venv/bin/python /home/ubuntu/git/GlucoseSaver/PoolingGlukose.py
Restart=always
User=ubuntu
WorkingDirectory=/home/ubuntu/git/GlucoseSaver
StandardOutput=journal
StandardError=journal
[Install]
WantedBy=multi-user.target

# /etc/systemd/system/glucose_api.service
[Unit]
Description=My Python Service
After=network.target

[Service]
Type=simple
ExecStart=/home/ubuntu/git/GlucoseSaver/.venv/bin/uvicorn GlukoseAPI:app --host 0.0.0.0 --port 8088
Restart=always
User=ubuntu
WorkingDirectory=/home/ubuntu/git/GlucoseSaver
StandardOutput=journal
StandardError=journal
[Install]
WantedBy=multi-user.target

# Run service commands
sudo systemctl daemon-reload
sudo systemctl enable glucose.service
sudo systemctl start glucose.service
# Check status
sudo systemctl status glucose.service
# Stop service
sudo systemctl stop glucose.service
# test script from venv
 sudo -u ubuntu /home/ubuntu/git/GlucoseSaver/.venv/bin/python /home/ubuntu/git/GlucoseSaver/PoolingGlukose.py
# usefull instalation for ifconfig
 sudo apt install net-tools
# set firewall ACCEPT
sudo iptables -L -n -v
sudo iptables -I INPUT -p tcp --dport 8088 -j ACCEPT
sudo netfilter-persistent save
# install Node22 on Ubuntu
sudo apt install npm
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
npm create vite@latest glucose-app -- --template react
cd glucose-app
npm run dev
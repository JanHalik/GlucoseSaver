# GlucoseSaver
# Pulls actual Glucose data from LibreLinkUp application.
On Ubuntu 24
python3 -m venv .venv
source .venv/bin/activate
pip3 install --no-input -r requirements.txt
python PollingGlukose.py
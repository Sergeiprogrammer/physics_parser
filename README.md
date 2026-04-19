# XML Event Analyzer

Local tool for analyzing ATLAS XML events.

## Features

- ZIP and XML support
- anomaly score
- manual score
- contrast score
- web interface (Flask)

## How it works

- Python core processes data
- Flask provides local UI
- No data is sent to the internet

## Run from source

```bash
pip install -r requirements.txt
python flask_app.py

Build EXE
pyinstaller --noconsole --add-data "templates;templates" flask_app.py
Security

This app runs locally and does not send data anywhere.


---
```

## How acces site
open url http://127.0.0.1:5000

## Easy install
just install exe from releases

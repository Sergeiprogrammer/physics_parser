# XML Event Analyzer

Local tool for analyzing ATLAS XML events.

# what it does?
**its analyze xml data from Paricles acelerator ATLAS (part of CERN) write data and measure how intresting it on deferent levels  
basicly you can fast navigate and a lot of events sort it look at their data and then analyze thme more precise**

## Features

- ZIP and XML support
- anomaly score
- manual score
- contrast score
- web interface (Flask)

# Score Guide

## Overview

### 🔴 Anomaly Score  
**How unusual is the event?**

Anomaly Score measures how far an event stands out from more typical events.  
It rewards extreme or rare-looking values.

---

### 🟢 Manual Score  
**How clean and plausible is the event?**

Manual Score imitates a more human-style evaluation.  
It prefers events that look physically cleaner and more reasonable.

---

### 🔵 Contrast Score  
**How interesting is the event?**

Contrast Score looks for events with a strong signal but not too much clutter.  
It is especially useful for finding compact yet striking events.

---

# 🔴 1. Anomaly Score

**Main idea:** detect events with extreme or unusual values.

### What it uses

- Very low or very high number of tracks  
- Very high maximum track transverse momentum (`max_track_pt`)  
- Very high total track transverse momentum (`sum_track_pt`)  
- High missing transverse energy (MET, stored as `etmis`)  
- Strong leading jet energy and a high number of jets  

### How to interpret it

A higher **Anomaly Score** means the event is more extreme and more likely to stand out.  
It does **not** automatically mean the event is clean or physically convincing.  
It simply means it looks unusual.

---

# 🟢 2. Manual Score

**Main idea:** imitate a hand-tuned, human-style quality check.

### What it uses

- Track count  
- Presence of both positive and negative tracks  
- Charge balance between positive and negative tracks  
- Maximum track momentum and total track momentum  
- Primary vertex position and vertex track ratio  
- MET level  
- Jet count and leading jet energy  

### How to interpret it

A higher **Manual Score** usually means the event looks cleaner, more balanced,  
and more physically reasonable according to the rule-based logic.

This score is useful when you want events that are easier to inspect  
and less likely to be pure noise.

---

# 🔵 3. Contrast Score

**Main idea:** find events with strong signal features but not too much activity around them.

### Core formula


contrast_score = scarcity × signal_strength × 10 − noise_penalty


### Its parts

- **Scarcity:** fewer tracks → higher value  
- **Signal strength:** based on MET, leading jet energy, and max track momentum  
- **Noise penalty:** subtracts points for:
  - too many tracks  
  - too many jets  
  - too much total activity  

### How to interpret it

A higher **Contrast Score** means the event is compact but still contains a noticeable signal.  
In practice, this often makes it one of the most useful scores for browsing and ranking interesting events.

---

# 📊 How to use the scores together

| Goal | Best score to check first | Why |
|------|--------------------------|-----|
| Find rare or extreme events | **Anomaly Score** | Highlights strong deviations and outliers |
| Find clean and physically reasonable events | **Manual Score** | Prefers balance and cleaner structure |
| Find interesting candidates quickly | **Contrast Score** | Focuses on strong signal with low noise |

👉 Recommended workflow:  
Sort by **Contrast Score** first, then inspect **Anomaly Score** and **Manual Score**.

---

# 🧠 Short summary

- **Anomaly Score** → how much the event stands out  
- **Manual Score** → how clean and plausible the event looks  
- **Contrast Score** → how interesting the event is for inspection 


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

##Easy install

Download the executable from Releases:

👉 https://github.com/Sergeiprogrammer/physics_parser/releases/tag/v1.0

Run analyzer.exe and the browser will open automatically.

## How it works

- Python core processes data
- Flask provides local UI
- No data is sent to the internet

# XML Event Analyzer

Local tool for analyzing ATLAS XML events.

---

# What does it do?

This tool analyzes XML data from the ATLAS particle detector (CERN).

It processes event data and evaluates how interesting each event is using different scoring methods.

You can quickly:
- browse large numbers of events
- sort them by different scores
- inspect their data
- select interesting candidates for deeper analysis

---

# Use case

This tool helps you quickly identify interesting events.

Typical workflow:
1. Analyze a dataset using this tool  
2. Sort events by score (e.g. Contrast Score)  
3. Select the most interesting events  
4. Use other software for detailed visualization and analysis  

---

# Features

- ZIP and XML support  
- Anomaly Score  
- Manual Score  
- Contrast Score  
- Web interface (Flask)  

---

# Score Guide

## Overview

### 🔴 Anomaly Score  
**How unusual is the event?**

Measures how much an event stands out from typical data.  
Rewards extreme or rare values.

---

### 🟢 Manual Score  
**How clean and plausible is the event?**

Simulates a human-style evaluation.  
Prefers physically clean and well-structured events.

---

### 🔵 Contrast Score  
**How interesting is the event?**

Finds events with strong signals but low noise.  
Useful for spotting compact and interesting events.

---

## 🔴 1. Anomaly Score

**Main idea:** detect unusual or extreme events.

### What it uses

- Track count extremes  
- High `max_track_pt`  
- High `sum_track_pt`  
- High MET (`etmis`)  
- Strong jets  

### Interpretation

Higher score → more unusual event  
(Not necessarily physically clean)

---

## 🟢 2. Manual Score

**Main idea:** human-like quality evaluation

### What it uses

- Track balance (+ / −)  
- Charge symmetry  
- Vertex quality  
- MET  
- Jets  

### Interpretation

Higher score → cleaner and more realistic event  

---

## 🔵 3. Contrast Score

**Main idea:** strong signal with minimal noise

### Formula

```

contrast_score = scarcity × signal_strength × 10 − noise_penalty

````

### Components

- **Scarcity:** fewer tracks → higher value  
- **Signal:** MET + jets + track energy  
- **Noise penalty:** too many tracks/jets  

### Interpretation

Higher score → compact and interesting event  

---

## 📊 How to use scores

| Goal | Best score | Why |
|------|-----------|-----|
| Find unusual events | Anomaly | Detects outliers |
| Find clean events | Manual | Physically reasonable |
| Find best candidates | Contrast | Strong signal, low noise |

👉 Recommended workflow:  
Sort by **Contrast Score**, then inspect others.

---

## 🧠 Summary

- Anomaly → unusual  
- Manual → clean  
- Contrast → interesting  

---

## Run from source

```bash
pip install -r requirements.txt
python flask_app.py
````

Open:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Build EXE

```bash
pyinstaller --noconsole --add-data "templates;templates" flask_app.py
```

---

## Easy install

Download from Releases:

👉 [https://github.com/Sergeiprogrammer/physics_parser/releases/tag/v1.0](https://github.com/Sergeiprogrammer/physics_parser/releases/tag/v1.0)

Run `analyzer.exe` — browser will open automatically.

---

## Security

* Runs locally
* No internet connection required
* Source code is open

---

## How it works

- Python core processes the data  
- Flask provides the web interface  

---

## Where to get datasets

You can find example datasets here:

👉 https://opendata.cern/search?q=&f=type%3ADataset&f=experiment%3AATLAS&l=list&order=desc&p=1&s=10&sort=mostrecent

---

---

## Where to get software

You can find software:

👉 https://atlas.cern/Resources/Event-Analysis-Tools

---

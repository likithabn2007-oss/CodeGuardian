# EquiCode Scanner: Static PR Auditor

EquiCode Scanner is an automated, rule-based static analysis tool that acts as an engineering guardrail. It scans Pull Request code snippets for security vulnerabilities (hardcoded secrets, unsafe SQL), accessibility issues (missing image alt-text) and non-inclusive language, and saves review metrics for the team. It works offline, with no API keys.

## The Problem
Code reviews are slow and inconsistent. Security slips, accessibility, and non-inclusive terminology are easy to miss, and they build up as tech debt. EquiCode catches them automatically before code is merged.

## Features
- Detects hardcoded secrets and string-built SQL queries
- Flags missing alt-text on images
- Replaces non-inclusive terms (e.g. "slave" -> "replica", "blacklist" -> "denylist")
- Scores each PR for security, accessibility and inclusivity
- Saves results to a database and shows them on a Streamlit dashboard

## Tech Stack
Python, Streamlit, MySQL (PyMySQL, SQLAlchemy), Pandas, Plotly

## Prerequisites
- Python 3.8+
- MySQL installed and running locally

## Setup

### 1. Get the code
```
git clone https://github.com/likithabn2007-oss/CodeGuardian.git
cd CodeGuardian
```

### 2. Create the database
Open MySQL Command Line or Workbench and run:

```sql
CREATE DATABASE IF NOT EXISTS equicode_db;
USE equicode_db;

CREATE TABLE IF NOT EXISTS pr_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    pr_title VARCHAR(255) NOT NULL,
    security_score INT NOT NULL,
    accessibility_score INT NOT NULL,
    inclusivity_score INT NOT NULL,
    ai_analysis JSON NOT NULL,
    refactored_code TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Install dependencies
```
pip install streamlit pymysql sqlalchemy pandas plotly
```

### 4. Run the app
Run from Command Prompt or a terminal (not Python IDLE):

```
cd path\to\your\folder
set DB_PASS=your_mysql_password
streamlit run app.py
```
(The default MySQL password in the code is `password`. Only set `DB_PASS` if yours is different. On Mac/Linux use `export DB_PASS=...`.)

The app opens at http://localhost:8501

## Demo Data
Paste this into the code box and click **Run Static Scan**:

```python
def load_dashboard_data(user_id):
    # Connect to the slave database for read-only metrics
    api_key = "sk_live_88442299"

    # Check if user is on the blacklist for abuse
    blacklist_users = [104, 109, 205]
    if user_id in blacklist_users:
        return "User account restricted."

    # Fetch all records for the dashboard view
    query = "SELECT * FROM user_metrics WHERE id = " + str(user_id)

    # Render the UI header
    ui_component = """
    <div class="header">
        <img src="dashboard_logo.png">
        <h1>Welcome to the Metrics Panel</h1>
    </div>
    """

    return ui_component
```

The scanner catches the hardcoded secret, flags the unsafe SQL, fixes the non-inclusive terms and flags the missing alt-text.

## Demo
- Video: https://drive.google.com/file/d/1_FcEH-Q3SK762VHLfHLwNeeYPTN5xvTf/view?usp=sharing
- Slides: https://drive.google.com/file/d/1okH94g1_xokXHqhovFGSJp4h_02k39eT/view?usp=sharing

## Team
Built by Likitha B N, Vedanth Mandanna , Aniruddhan for the RVAHack26. Our first hackathon!

## What's Next
- Add an AI layer to explain findings and suggest fixes
- Support more languages and rule sets
- GitHub integration to scan PRs automatically

    
   

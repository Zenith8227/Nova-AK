# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, jsonify
import sqlite3
import datetime
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = "nexus_unlimited_trading_999"

# اپنی Groq API Key یہاں درج کریں
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

# ----------------- Database Setup -----------------
def init_db():
    try:
        conn = sqlite3.connect('nexus_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_ip TEXT,
                user_message TEXT,
                ai_reply TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Init Error:", e)

def save_chat_log(user_ip, user_msg, ai_reply):
    try:
        conn = sqlite3.connect('nexus_logs.db')
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO chat_logs (user_ip, user_message, ai_reply, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_ip, user_msg, ai_reply, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Save Error:", e)

init_db()

# ----------------- Frontend Dashboard Route -----------------
@app.route("/")
def nexus_home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ur" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Amir AI Trading & Admin Hub</title>
        <style>
            :root {
                --bg-color: #070a14;
                --panel-bg: #0f172a;
                --text-color: #ffffff;
                --accent-color: #d97706; /* Gold Trading Vibe */
                --border-color: rgba(217, 119, 6, 0.3);
                --up-color: #22c55e;
                --down-color: #ef4444;
            }
            body {
                background: var(--bg-color);
                color: var(--text-color);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            header {
                background: var(--panel-bg);
                padding: 15px 20px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            h2 { margin: 0; font-size: 18px; color: var(--accent-color); text-transform: uppercase; letter-spacing: 1px; }
            .tabs {
                display: flex;
                background: var(--panel-bg);
                border-bottom: 1px solid var(--border-color);
                flex-wrap: wrap;
            }
            .tab-btn {
                flex: 1;
                padding: 12px;
                background: none;
                border: none;
                color: var(--text-color);
                font-weight: bold;
                cursor: pointer;
                text-align: center;
                border-bottom: 2px solid transparent;
            }
            .tab-btn.active {
                color: var(--accent-color);
                border-bottom: 2px solid var(--accent-color);
            }
            .content-section {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                display: none;
                max-width: 800px;
                width: 100%;
                margin: 0 auto;
                box-sizing: border-box;
            }
            .content-section.active {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            /* Chat Styles */
            .chat-container {
                flex: 1;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 12px;
                padding-bottom: 10px;
                max-height: 60vh;
            }
            .message {
                padding: 12px 16px;
                border-radius: 12px;
                max-width: 85%;
                line-height: 1.5;
                word-wrap: break-word;
                font-size: 15px;
            }
            .user-msg { background: var(--accent-color); color: #fff; align-self: flex-end; }
            .ai-msg { background: var(--panel-bg); border: 1px solid var(--border-color); align-self: flex-start; }
            
            /* Trading Signal Styles */
            .signal-card {
                background: var(--panel-bg);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }
            .signal-badge {
                font-size: 22px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                display: inline-block;
                margin: 15px 0;
            }
            .signal-up { background: rgba(34, 197, 94, 0.2); color: var(--up-color); border: 1px solid var(--up-color); }
            .signal-down { background: rgba(239, 68, 68, 0.2); color: var(--down-color); border: 1px solid var(--down-color); }
            
            /* Admin Panel Styles */
            .admin-table {
                width: 100%;
                border-collapse: collapse;
                background: var(--panel-bg);
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid var(--border-color);
            }
            .admin-table th, .admin-table td {
                padding: 10px;
                border-bottom: 1px solid var(--border-color);
                text-align: left;
                font-size: 14px;
            }
            .admin-table th { color: var(--accent-color); background: #070a14; }

            .input-box {
                background: var(--panel-bg);
                padding: 12px 15px;
                border-top: 1px solid var(--border-color);
                display: flex;
                gap: 10px;
                max-width: 800px;
                width: 100%;
                margin: 0 auto;
                box-sizing: border-box;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px;
                background: var(--bg-color);
                border: 1px solid var(--border-color);
                color: var(--text-color);
                border-radius: 8px;
                outline: none;
                font-size: 15px;
            }
            .btn-main {
                background: var(--accent-color);
                color: #fff;
                border: none;
                padding: 0 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <header>
            <h2>⚡ Amir AI Hub & Admin</h2>
            <button class="btn-main" onclick="toggleMusic()">🎵 Music</button>
        </header>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('trading', this)">📊 Market Signals</button>
            <button class="tab-btn" onclick="switchTab('chat', this)">💬 AI Chat</button>
            <button class="tab-btn" onclick="switchTab('admin', this); loadAdminLogs();">⚙️ Admin Panel</button>
        </div>

        <!-- Trading Signal Section -->
        <div id="trading-section" class="content-section active">
            <div class="signal-card">
                <h3>Gold & Forex Live Analyzer</h3>
                <p>AI institutional desk engine scanning live market trends...</p>
                <div id="signalDisplay" class="signal-badge signal-up">READY</div>
                <p id="analysisReason">بٹن دبائیں اور لائیو مارکیٹ کا تجزیہ حاصل کریں۔</p>
                <button class="btn-main" style="padding: 12px 25px; width: 100%; margin-top: 10px;" onclick="getTradingSignal()">مارکیٹ سگنل چیک کریں (Analyze)</button>
            </div>
        </div>

        <!-- Chat Section -->
        <div id="chat-section" class="content-section">
            <div class="chat-container" id="chatBox">
                <div class="message ai-msg">السلام علیکم! میں آپ کا انلمیٹڈ اے آئی اسسٹنٹ ہوں۔ مارکیٹ، ٹریڈنگ یا کسی بھی موضوع پر جو چاہیں پوچھیں۔</div>
            </div>
            <div class="input-box" style="position: relative; max-width: 100%; margin:0;">
                <input type="text" id="userInput" placeholder="یہاں اپنا سوال کھل کر پوچھیں..." onkeypress="handleKeyPress(event)">
                <button class="btn-main" onclick="sendMessage()">ارسال</button>
            </div>
        </div>

        <!-- Admin Panel Section -->
        <div id="admin-section" class="content-section">
            <h3>Admin Chat Logs Panel</h3>
            <p>تمام صارفین کی چیٹ ہسٹری یہاں محفوظ ہوتی ہے:</p>
            <div style="overflow-x:auto;">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>IP</th>
                            <th>User Message</th>
                            <th>AI Reply</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="adminLogsBody">
                        <tr><td colspan="5" style="text-align:center;">لوڈ ہو رہا ہے...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <audio id="lofiAudio" loop src="https://stream.zeno.fm/f3wvbbqmdg8uv"></audio>

        <script>
            let musicPlaying = false;
            function toggleMusic() {
                const audio = document.getElementById('lofiAudio');
                if (musicPlaying) { audio.pause(); musicPlaying = false; }
                else { audio.play(); musicPlaying = true; }
            }

            function switchTab(tabName, btn) {
                document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.getElementById(tabName + '-section').classList.add('active');
                btn.classList.add('active');
            }

            function getTradingSignal() {
                const display = document.getElementById('signalDisplay');
                const reason = document.getElementById('analysisReason');
                display.innerText = "ANALYZING...";
                display.className = "signal-badge";
                reason.innerText = "مارکیٹ کا تجزیہ کیا جا رہا ہے...";

                fetch('/analyze', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    display.innerText = data.signal;
                    if (data.signal.includes("UP") || data.signal.includes("BUY")) {
                        display.className = "signal-badge signal-up";
                    } else {
                        display.className = "signal-badge signal-down";
                    }
                    reason.innerText = data.reason;
                })
                .catch(err => {
                    display.innerText = "ERROR";
                    reason.innerText = "سرور سے رابطہ نہیں ہو سکا۔";
                });
            }

            function loadAdminLogs() {
                fetch('/admin/logs')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.getElementById('adminLogsBody');
                    tbody.innerHTML = "";
                    if(data.logs.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">کوئی ریکارڈ موجود نہیں۔</td></tr>`;
                        return;
                    }
                    data.logs.forEach(row => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${row[0]}</td>
                                <td>${row[1]}</td>
                                <td>${row[2]}</td>
                                <td>${row[3]}</td>
                                <td>${row[4]}</td>
                            </tr>
                        `;
                    });
                })
                .catch(err => {
                    console.error("Admin logs load error:", err);
                });
            }

            function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

            function sendMessage() {
                const input = document.getElementById('userInput');
                const text = input.value.trim();
                if (!text) return;

                const chatBox = document.getElementById('chatBox');
                chatBox.innerHTML += `<div class="message user-msg">${text}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                })
                .then(res => res.json())
                .then(data => {
                    chatBox.innerHTML += `<div class="message ai-msg">${data.reply}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch(err => {
                    chatBox.innerHTML += `<div class="message ai-msg" style="color:red;">رابطہ ٹوٹ گیا۔</div>`;
                });
            }
        </script>
    </body>
    </html>
    """)

# ----------------- Market Analyzer Backend API -----------------
@app.route("/analyze", methods=["POST"])
def analyze_market():
    try:
        req_data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Analyze current forex/gold market technical setup. Reply in strict format: SIGNAL: [UP or DOWN] - REASON: [Detailed analysis in Urdu]"}]
        }
        
        req_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(req_data).encode("utf-8"),
            headers=req_headers,
            method="POST"
        )

        signal = "📈 SIGNAL: BUY (UP)"
        reason = "مارکیٹ کا ٹرینڈ بلش ہے، سپورٹ لیول سے اوپر جانے کے قوی امکانات ہیں۔"
        
        try:
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                if "choices" in res_json:
                    content = res_json["choices"][0]["message"]["content"]
                    if "DOWN" in content.upper() or "SELL" in content.upper():
                        signal = "📉 SIGNAL: SELL (DOWN)"
                    else:
                        signal = "📈 SIGNAL: BUY (UP)"
                    reason = content
        except Exception as api_err:
            reason = f"تجزیہ حاصل کرنے میں مسئلہ پیش آیا۔"

        return jsonify({"signal": signal, "reason": reason})
    except Exception as e:
        return jsonify({"signal": "⚠️ HOLD", "reason": f"Error: {str(e)}"})

# ----------------- Unlimited Chat Backend API -----------------
@app.route("/chat", methods=["POST"])
def chat_handler():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        user_ip = request.remote_addr

        req_data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": user_message}]
        }
        
        req_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(req_data).encode("utf-8"),
            headers=req_headers,
            method="POST"
        )

        ai_reply = "معذرت، سرور سے رابطہ نہیں ہو سکا۔"
        try:
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                if "choices" in res_json:
                    ai_reply = res_json["choices"][0]["message"]["content"]
        except Exception as api_err:
            ai_reply = f"جی ہاں، آپ کا سوال سنا گیا: '{user_message}'۔"

        # Database میں گفتگو محفوظ کریں
        save_chat_log(user_ip, user_message, ai_reply)

        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"System Error: {str(e)}"})

# ----------------- Admin Panel API Route -----------------
@app.route("/admin/logs", methods=["GET"])
def admin_logs():
    try:
        conn = sqlite3.connect('nexus_logs.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_ip, user_message, ai_reply, timestamp FROM chat_logs ORDER BY id DESC LIMIT 50")
        logs = cursor.fetchall()
        conn.close()
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"logs": []})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

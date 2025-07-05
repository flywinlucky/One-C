from telethon import TelegramClient, events
import asyncio
import json
import webbrowser
import os

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
      max-width: 1100px;
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
    <div class="leads-grid">
      {cards}
    </div>
  </div>
</body>
</html>
"""

def lead_to_card_html(lead):
    c = lead["client"]
    info = (
        f"Nume: {c.get('full_name','')}\n"
        f"Țara: {c.get('country','')}\n"
        f"Lucrează: {'Da' if c.get('employed') else 'Nu'}\n"
        f"Suma solicitată: {c.get('requested_amount','')}"
    )
    telegram = c.get('telegram', '')
    return f"""
    <div class="lead-card">
      <div class="lead-id">Lead ID: {lead['lead_id']}</div>
      <div class="lead-date">Data: {lead['date']} &nbsp; Ora: {lead['time']}</div>
      <div class="lead-info">{info}</div>
      <div class="lead-telegram">Telegram: {telegram}</div>
    </div>
    """

def parse_leads_from_messages(messages):
    leads = []
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
                leads.append(data)
        except Exception:
            continue
    return leads

async def fetch_leads():
    client = TelegramClient('session_adminpanel', API_ID, API_HASH)
    await client.start(PHONE_NUMBER)
    bot_entity = await client.get_entity(BOT_USERNAME)
    messages = []
    async for msg in client.iter_messages(bot_entity, limit=500):
        messages.append(msg)
    await client.disconnect()
    return parse_leads_from_messages(messages)

def main():
    print("Se extrag lead-urile din Telegram...")
    try:
        leads = asyncio.run(fetch_leads())
    except Exception as e:
        print("Eroare la conectare sau extragere mesaje:", e)
        return

    cards_html = "\n".join([lead_to_card_html(lead) for lead in leads]) if leads else "<div style='color:#fff;font-size:1.2rem;'>Nu există lead-uri găsite.</div>"
    html = HTML_TEMPLATE.format(cards=cards_html)

    out_path = os.path.join(os.path.dirname(__file__), "leads_dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard generat: {out_path}")
    webbrowser.open("file://" + os.path.abspath(out_path))

if __name__ == "__main__":
    main()
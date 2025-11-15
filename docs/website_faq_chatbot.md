# Website FAQ Chatbot (No-Code Friendly)

Non-technical teams can embed the `/support-bot/query` endpoint on any marketing site using a lightweight JS widget. Follow these steps during handoff:

## 1. Deploy the API

1. Provision a small VM or container host (Render, Railway, Fly.io, etc.).
2. Copy `.env.example` → `.env`, add your API key + `SUPPORT_BOT_COLLECTION` path, and run:
   ```bash
   docker run -d --name support-bot -p 443:8000 \
     --env-file .env ghcr.io/razonin4k/chatbot-templates:latest
   ```
3. Place the service behind HTTPS (e.g., Render auto TLS or Caddy/NGINX).

## 2. Expose a Minimal Widget

Drop this snippet into the site's `<head>` or via a CMS HTML block. Update `API_BASE_URL` to the HTTPS origin that hosts your FastAPI app.

```html
<div id="faq-bot"></div>
<script>
  const API_BASE_URL = "https://support.yourdomain.com";

  const container = document.getElementById("faq-bot");
  container.innerHTML = `
    <style>
      #faq-bot-widget { font-family: sans-serif; border: 1px solid #ddd; padding: 16px; max-width: 360px; }
      #faq-bot-widget textarea { width: 100%; min-height: 80px; }
      #faq-bot-response { margin-top: 12px; }
    </style>
    <div id="faq-bot-widget">
      <h4>Need help?</h4>
      <textarea id="faq-bot-message" placeholder="Ask about pricing or onboarding..."></textarea>
      <button id="faq-bot-send">Ask SupportBot</button>
      <div id="faq-bot-response"></div>
    </div>`;

  async function askBot() {
    const message = document.getElementById("faq-bot-message").value.trim();
    if (!message) return;
    const responseArea = document.getElementById("faq-bot-response");
    responseArea.textContent = "Thinking...";

    try {
      const res = await fetch(`${API_BASE_URL}/support-bot/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "web-widget", message })
      });
      const data = await res.json();
      responseArea.textContent = data.answer;
    } catch (error) {
      responseArea.textContent = "We're offline right now. Email support@yourdomain.com.";
    }
  }

  document.getElementById("faq-bot-send").addEventListener("click", askBot);
</script>
```

## 3. Style & Telemetry

- Update the CSS block to match the brand system.
- Replace the hard-coded `user_id` with a per-session hash if you need attribution.
- Inspect anonymized usage metrics in `analytics/support_metrics.json` to see question volume and fallback rate before/after launch.

# Loom Script – Multi-Tenant FAQ Chatbot

## Demo Tenants Overview

Use these tenant personas in scripts and proposals:

1. **FlowWell Yoga Studio (B2C)**
   - Docs/FAQs: class schedule, membership tiers, cancellation policy, instructor bios, studio etiquette.
   - Sample questions:
     - "What's the difference between Unlimited and 10-class pack?"
     - "Can I cancel tomorrow's hot yoga session?"
   - Good answers: mention pricing, cancellation window (e.g., 12 hours), etiquette (arrive early, mats available).

2. **Nimbus B2B SaaS Platform (B2B)**
   - Docs: onboarding timeline, sandbox provisioning, SSO/Okta setup, SLA table, analytics export.
   - Sample questions: onboarding length, sandbox requests, SLA for P1s, exporting usage analytics.
   - Good answers: 2-week onboarding, sandbox via support portal, SLA table, settings → reports path, CSM involvement.

3. **IntraTech Internal IT Helpdesk (Internal)**
   - Docs: PTO process, incident response, system access policy, release cadence, VPN troubleshooting.
   - Sample questions: getting prod access, who to page for sev1, release windows, how to request PTO.
   - Good answers: SOC2 training + Okta SSO, PagerDuty/on-call, Tue/Thu windows, PTO via HR tool with notice.

---

## Video Script Outline

**Goal:** 3–4 minute demo of the FastAPI + RAG + multi-tenant FAQ bot.

### 1. Intro (0:00–0:20)
"Hey, it's David. I'll walk you through our multi-tenant FAQ chatbot template built with FastAPI, GPT-4, and Chroma. One deployment, multiple tenants."

### 2. Start the Server (0:20–1:00)
- On screen: `uvicorn server:app --reload`.
- "The `.env` holds LLM keys, default collection, and we have `config/support_tenants.json` for tenant-specific overrides like tone and fallback messages."

### 3. Tenant Demo 1 – Yoga Studio (1:00–1:40)
- On screen: HTTPie/curl call to `/support-bot/query` with `tenant_id=yoga`.
- Ask: "Can I cancel tomorrow's hot yoga class?"
- "The answer references the yoga cancellation policy and etiquette. Note `tenant_id` in the response and the yoga docs used under the hood."

### 4. Tenant Demo 2 – B2B SaaS (1:40–2:10)
- Similar call with `tenant_id=b2b_saas` and an onboarding question.
- "Here the bot talks about 2-week onboarding, sandbox, and SLAs—same engine, different corpus and system prompt."

### 5. Website Embed Snippet (2:10–2:50)
- On screen: `docs/website_faq_chatbot.md` or HTML snippet.
- "Non-technical teams can paste this in Webflow/Squarespace, set `API_BASE_URL`, and customize styles. No extra backend work needed."

### 6. Analytics & Privacy (2:50–3:30)
- On screen: `scripts/analyze_support_metrics.py` output.
- "We track fallback rate and response latency per tenant. Metrics anonymize questions (no raw text), so this is safe for GDPR/PII."

### 7. Wrap (3:30–3:50)
"So with one deployment you serve yoga studios, SaaS platforms, and internal IT. If you want this for your org, you can plug in your docs and go live quickly."

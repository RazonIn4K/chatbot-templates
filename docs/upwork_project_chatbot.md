# Website FAQ Chatbot with GPT-4 & RAG (Multi-tenant)

**Description:**
Deliver a production-ready FAQ chatbot powered by GPT-4/Claude, FastAPI, and Retrieval-Augmented Generation. I ingest your existing documentation, deploy a tenant-aware API, provide a website widget, and hand over analytics + runbooks so your team owns the stack.

## Demo Tenants Overview

Reference these tenant personas for proposals and customization:

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

## Service Packages

### Basic – Website FAQ Bot (~1 week)
- Configure LLM provider and `.env`.
- Ingest a single FAQ knowledge base into Chroma.
- Deploy `/support-bot/query` + website embed snippet.
- Provide Postman collection + quickstart docs.

### Standard – Multi-Tenant + Analytics (~2 weeks)
- Everything in Basic.
- Multiple tenant collections/prompts.
- Analytics JSON + SLA reporting script.
- Multi-tenant runbook + Loom walkthrough.

### Premium – Internal Knowledge Assistant (~3 weeks)
- Everything in Standard.
- Internal handbook assistant (CLI + FastAPI demo).
- Security/privacy review (secrets, TLS, logging hygiene).
- Deployment playbooks + enablement session.

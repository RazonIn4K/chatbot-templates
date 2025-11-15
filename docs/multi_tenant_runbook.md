# Multi-Tenant Runbook

Use this guide when onboarding or updating tenants that share a single chatbot deployment.

## 1. Onboard a New Tenant
1. **Create knowledge base docs**
   - Add Markdown/TXT files under `docs/faq/<tenant>/` or point the ingest script to their folder.
2. **Update tenant config**
   - Edit `config/support_tenants.json` and add an entry:
     ```json
     {
       "tenant_id": "acme",
       "collection": "acme_faq",
       "top_k": 4,
       "fallback": "Acme Support will reply via email soon.",
       "system_prompt": "You are AcmeBot..."
     }
     ```
3. **Ingest documents into the tenant collection**
   ```bash
   python examples/simple_faq_rag/ingest_faq.py --docs-dir docs/faq/acme --collection acme_faq --reset
   ```
4. **Smoke test locally**
   ```bash
   uvicorn server:app --reload
   http POST :8000/support-bot/query user_id=acme-demo tenant_id=acme message="How do I reset my password?"
   ```
5. **Commit config/docs** so the tenant definition lives in Git.

## 2. Safe Update Process (Staging → Production)
1. **Branch + stage**
   - Create a feature branch and update docs/configs.
   - Deploy to staging (e.g., `staging.support.example.com`).
2. **Run regression tests**
   - `pytest`
   - Hit `/support-bot/query` for existing tenants + new tenant.
3. **Validate analytics**
   - Run the analytics CLI (see README) to ensure metrics file tracks per-tenant traffic.
4. **Promote**
   - Merge to main.
   - Deploy container/image to production environment (Render/Fly/EC2) using the same artifact tested in staging.
5. **Post-deploy checks**
   - Trigger a sample query per tenant in production.
   - Confirm new tenant appears in `analytics/support_metrics.json`.

## 3. Kickoff Checklist (Share With Clients)
- [ ] Identify tenant_id and desired chatbot tone/system prompt.
- [ ] Provide FAQ/internal docs (Markdown, Notion export, Google Doc).
- [ ] Approve fallback message + escalation path.
- [ ] Confirm hosting target (Render, Fly.io, AWS) and domain.
- [ ] Decide on logging/analytics cadence and who receives weekly exports.

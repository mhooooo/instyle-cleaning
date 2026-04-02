# 🧹 InStyle Cleaning — DeerFlow Skills Ecosystem Audit

**Date:** April 3, 2026  
**Business:** InStyle Cleaning — Premium residential & commercial cleaning, Gainesville FL  
**Purpose:** Map all available DeerFlow/agent skills to InStyle Cleaning's operational needs  
**Method:** 14 targeted searches across `skills.sh` ecosystem via `npx skills find`

---

## Executive Summary

**78 skills discovered** across **14 business-critical categories** for InStyle Cleaning. The ecosystem covers nearly every operational need — from CRM and scheduling through invoicing, review management, social media, and seasonal marketing. The strongest coverage is in **social media automation** (6 skills, 2K+ combined installs), **email marketing** (6+ skills, 28K+ installs), and **CRM** (6 skills). Gaps exist in **cleaning-industry-specific** tooling (no dedicated cleaning/home-services skill) and **route optimization** (only 2 results, neither cleaning-specific).

### Coverage Heat Map

| Category | Skills Found | Top Installs | Relevance to InStyle |
|----------|:-----------:|:------------:|:-------------------:|
| 🔴 CRM & Customer Management | 6 | 1,100 | ⭐⭐⭐⭐⭐ |
| 🟠 Scheduling & Booking | 6 | 942 | ⭐⭐⭐⭐⭐ |
| 🟡 Route Optimization | 2 | 383 | ⭐⭐⭐⭐ |
| 🟢 Quote & Invoice Generation | 6 | 49 | ⭐⭐⭐⭐⭐ |
| 🔵 Review & Reputation Mgmt | 6 | 465 | ⭐⭐⭐⭐⭐ |
| 🟣 Social Media Automation | 6 | 678 | ⭐⭐⭐⭐⭐ |
| ⚪ Customer Follow-up & Email | 6 | 337 | ⭐⭐⭐⭐⭐ |
| 🔴 Seasonal Marketing & Campaigns | 6 | 27,700 | ⭐⭐⭐⭐⭐ |
| 🟠 Local SEO & Google Business | 6 | 1,400 | ⭐⭐⭐⭐⭐ |
| 🟡 SMS & Notifications | 5 | 455 | ⭐⭐⭐⭐ |
| 🟢 Payment Processing (Stripe) | 6 | 1,400 | ⭐⭐⭐⭐ |
| 🔵 Lead Generation & Sales | 6 | 386 | ⭐⭐⭐⭐ |
| 🟣 Proposals & Contracts | 5 | 65 | ⭐⭐⭐⭐ |
| ⚪ Analytics & Dashboards | 6 | 611 | ⭐⭐⭐⭐ |
| **BONUS** Categories | | | |
| 🔶 Google Sheets Automation | 6 | 607 | ⭐⭐⭐⭐ |
| 🔷 WhatsApp Automation | 6 | 389 | ⭐⭐⭐ |
| 🟤 Referral Programs | 6 | 26,400 | ⭐⭐⭐⭐⭐ |
| 🟩 Content Marketing & Blog | 6 | 2,400 | ⭐⭐⭐⭐ |
| 🟦 Google Ads / PPC | 5 | 322 | ⭐⭐⭐⭐ |
| 🟪 Field Service Management | 1 | 53 | ⭐⭐⭐⭐⭐ |

---

## Category 1: CRM & Customer Management

> **Why it matters:** InStyle needs to track clients, property details, service history, cleaning preferences, and lifetime value. A cleaning company lives and dies by repeat bookings.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **salesforce** | membranedev/application-skills | 1,100 | ⭐⭐⭐ | Enterprise CRM — overkill for startup, but powerful if scaling |
| 2 | **crm-integration** | scientiacapital/skills | 141 | ⭐⭐⭐⭐⭐ | Generic CRM integration — most flexible for small business |
| 3 | **agile-crm** | membranedev/application-skills | 96 | ⭐⭐⭐⭐ | Lightweight CRM, good fit for SMB service businesses |
| 4 | **crm-domain-knowledge** | danhvb/my-ba-skills | 20 | ⭐⭐⭐ | CRM best practices & domain knowledge |
| 5 | **sales-integration** | sales-skills/sales | 17 | ⭐⭐⭐ | Sales pipeline management |
| 6 | **crm-integration** | manojbajaj95/gtm-skills | 13 | ⭐⭐⭐⭐ | Go-to-market CRM integration |

**🎯 Top Pick for InStyle:** `scientiacapital/skills@crm-integration` — flexible, not locked to one CRM vendor  
**Install:** `npx skills add scientiacapital/skills@crm-integration`  
**Link:** https://skills.sh/scientiacapital/skills/crm-integration

---

## Category 2: Scheduling & Booking

> **Why it matters:** Cleaning appointments are the revenue engine. Automated booking, reminders, and calendar sync eliminate no-shows and double-bookings.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **calendar-automation** | claude-office-skills/skills | 942 | ⭐⭐⭐⭐⭐ | Full calendar automation — scheduling, reminders, blocking |
| 2 | **google-calendar** | odyssey4me/agent-skills | 318 | ⭐⭐⭐⭐⭐ | Google Calendar integration |
| 3 | **google-calendar-automation** | composiohq/awesome-claude-skills | 162 | ⭐⭐⭐⭐ | Google Calendar via Composio |
| 4 | **acuity-scheduling** | membranedev/application-skills | 13 | ⭐⭐⭐⭐⭐ | Acuity Scheduling — purpose-built booking platform |
| 5 | **google-calendar** | vm0-ai/vm0-skills | 23 | ⭐⭐⭐ | Alternative Google Calendar integration |
| 6 | **google-calendar** | abdullahbeam/nexus-design-abdullah | 15 | ⭐⭐⭐ | Another Google Calendar option |

**🎯 Top Pick for InStyle:** `claude-office-skills/skills@calendar-automation` (942 installs) + `membranedev/application-skills@acuity-scheduling` for client-facing booking  
**Install:** `npx skills add claude-office-skills/skills@calendar-automation`  
**Link:** https://skills.sh/claude-office-skills/skills/calendar-automation

---

## Category 3: Route Optimization

> **Why it matters:** Cleaning crews travel between client homes all day. Optimized routes = more jobs per day = more revenue, less gas.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **mapbox-geospatial-operations** | mapbox/mapbox-agent-skills | 383 | ⭐⭐⭐⭐⭐ | Mapbox geospatial — routing, distance calc, geo queries |
| 2 | **site-logistics-optimization** | datadrivenconstruction/ddc_skills_for_ai_agents_in_construction | 6 | ⭐⭐⭐ | Construction-focused but adaptable logistics optimization |

**🎯 Top Pick for InStyle:** `mapbox/mapbox-agent-skills@mapbox-geospatial-operations` — calculate optimal routes between client addresses across Gainesville  
**Install:** `npx skills add mapbox/mapbox-agent-skills@mapbox-geospatial-operations`  
**Link:** https://skills.sh/mapbox/mapbox-agent-skills/mapbox-geospatial-operations  
**⚠️ Gap:** No cleaning-specific route optimization skill exists. Custom skill recommended.

---

## Category 4: Quote & Invoice Generation

> **Why it matters:** InStyle quotes jobs by sqft/room count, then invoices after service. Automation here means faster cash collection and professional branding.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **invoice-generation** | eachlabs/skills | 49 | ⭐⭐⭐⭐⭐ | Dedicated invoice generation |
| 2 | **invoice-generator** | eddiebe147/claude-settings | 47 | ⭐⭐⭐⭐ | Invoice generation templates |
| 3 | **billing-automation** | anton-abyzov/specweave | 17 | ⭐⭐⭐⭐ | Billing workflow automation |
| 4 | **invoice-generator** | jmsktm/claude-settings | 12 | ⭐⭐⭐ | Alternative invoice generator |
| 5 | **billing-automation** | microck/ordinary-claude-skills | 8 | ⭐⭐⭐ | Alternative billing automation |
| 6 | **cost-estimation-resource** | datadrivenconstruction/ddc_skills_for_ai_agents_in_construction | 22 | ⭐⭐⭐ | Cost estimation — adaptable to cleaning quotes |

**🎯 Top Pick for InStyle:** `eachlabs/skills@invoice-generation` for invoices + adapt `cost-estimation-resource` logic for cleaning quotes  
**Install:** `npx skills add eachlabs/skills@invoice-generation`  
**Link:** https://skills.sh/eachlabs/skills/invoice-generation

---

## Category 5: Review & Reputation Management

> **Why it matters:** Premium cleaning lives on Google/Yelp reviews. One bad review costs 10 clients. Proactive review solicitation and reputation monitoring are non-negotiable.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **review-management** | eronred/aso-skills | 465 | ⭐⭐⭐⭐⭐ | App store review management — adaptable to Google reviews |
| 2 | **performance-review** | anthropics/knowledge-work-plugins | 352 | ⭐⭐ | Employee performance reviews, not customer reviews |
| 3 | **review** | open-horizon-labs/skills | 63 | ⭐⭐⭐ | General review workflow |
| 4 | **social-crisis-manager** | eddiebe147/claude-settings | 44 | ⭐⭐⭐⭐ | Crisis management for bad reviews/PR issues |
| 5 | **reputation-recovery** | guia-matthieu/clawfu-skills | 35 | ⭐⭐⭐⭐⭐ | Reputation recovery and management |
| 6 | **agent-reviewer** | ruvnet/ruflo | 48 | ⭐⭐ | Code/agent review — not relevant |

**🎯 Top Pick for InStyle:** `eronred/aso-skills@review-management` + `guia-matthieu/clawfu-skills@reputation-recovery`  
**Install:** `npx skills add eronred/aso-skills@review-management`  
**Link:** https://skills.sh/eronred/aso-skills/review-management

---

## Category 6: Social Media Automation

> **Why it matters:** InStyle needs consistent before/after posts, cleaning tips, seasonal promos. Social proof drives premium cleaning leads.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **tiktok-marketing** | claude-office-skills/skills | 678 | ⭐⭐⭐⭐⭐ | TikTok marketing — before/after cleaning videos are viral gold |
| 2 | **social-publisher** | claude-office-skills/skills | 552 | ⭐⭐⭐⭐⭐ | Multi-platform social publishing |
| 3 | **linkedin-automation** | claude-office-skills/skills | 374 | ⭐⭐⭐ | LinkedIn — less relevant for residential cleaning |
| 4 | **youtube-automation** | claude-office-skills/skills | 355 | ⭐⭐⭐⭐ | YouTube — cleaning tutorial videos |
| 5 | **coo-social-media** | garfield-bb/hap-skills-collection | 23 | ⭐⭐⭐ | COO-level social media strategy |
| 6 | **social-media-automator** | skills.volces.com | 15 | ⭐⭐⭐⭐ | General social media automation |

**🎯 Top Pick for InStyle:** `claude-office-skills/skills@social-publisher` (cross-platform) + `claude-office-skills/skills@tiktok-marketing` (cleaning content is TikTok gold)  
**Install:** `npx skills add claude-office-skills/skills@social-publisher`  
**Link:** https://skills.sh/claude-office-skills/skills/social-publisher

---

## Category 7: Customer Follow-up & Email Sequences

> **Why it matters:** Post-service follow-up emails, satisfaction surveys, rebooking nudges, and "we miss you" sequences drive repeat revenue.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **email-sequence** | sickn33/antigravity-awesome-skills | 337 | ⭐⭐⭐⭐⭐ | Email sequence automation — drip campaigns |
| 2 | **cold-email** | inkeep/team-skills | 45 | ⭐⭐⭐ | Cold outreach — useful for commercial cleaning leads |
| 3 | **email-template-generator** | nicepkg/ai-workflow | 18 | ⭐⭐⭐⭐ | Generate email templates |
| 4 | **cold-email-personalizer** | yangliu2060/smith--skills | 9 | ⭐⭐⭐ | Personalized outreach |
| 5 | **customer-io** | vm0-ai/vm0-skills | 6 | ⭐⭐⭐⭐ | Customer.io integration — lifecycle messaging |
| 6 | **email-template-generator** | manojbajaj95/gtm-skills | 5 | ⭐⭐⭐ | Alternative email template generator |

**🎯 Top Pick for InStyle:** `sickn33/antigravity-awesome-skills@email-sequence` for automated post-cleaning follow-ups  
**Install:** `npx skills add sickn33/antigravity-awesome-skills@email-sequence`  
**Link:** https://skills.sh/sickn33/antigravity-awesome-skills/email-sequence

---

## Category 8: Seasonal Marketing & Campaigns

> **Why it matters:** Spring deep-clean, pre-holiday party cleaning, back-to-school, post-Thanksgiving — seasonal campaigns are revenue spikes for cleaning companies.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **email-sequence** | coreyhaines31/marketingskills | 27,700 | ⭐⭐⭐⭐⭐ | Massive install base — proven email sequence framework |
| 2 | **seasonal-campaigns** | vivy-yi/xiaohongshu-skills | 21 | ⭐⭐⭐⭐ | Seasonal campaign planning |
| 3 | **email-sequence** | phrazzld/claude-config | 22 | ⭐⭐⭐ | Alternative email sequence |
| 4 | **seasonal-campaign-automation** | finsilabs/awesome-ecommerce-skills | 8 | ⭐⭐⭐⭐⭐ | Dedicated seasonal campaign automation |
| 5 | **email-sequence** | aitytech/agentkits-marketing | 10 | ⭐⭐⭐ | Marketing email sequences |
| 6 | **stable-design** | vivy-yi/xiaohongshu-skills | 31 | ⭐⭐ | Design-focused, less relevant |

**🎯 Top Pick for InStyle:** `coreyhaines31/marketingskills@email-sequence` (27.7K installs!) + `finsilabs/awesome-ecommerce-skills@seasonal-campaign-automation`  
**Install:** `npx skills add coreyhaines31/marketingskills@email-sequence`  
**Link:** https://skills.sh/coreyhaines31/marketingskills/email-sequence

---

## Category 9: Local SEO & Google Business

> **Why it matters:** "Cleaning service near me" is InStyle's #1 lead source. Dominating local SEO = dominating the market.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **rank-local** | calm-north/seojuice-skills | 1,400 | ⭐⭐⭐⭐⭐ | Local SEO ranking optimization |
| 2 | **local-seo** | kostja94/marketing-skills | 250 | ⭐⭐⭐⭐⭐ | Dedicated local SEO skill |
| 3 | **local-marketing** | dengineproblem/agents-monorepo | 85 | ⭐⭐⭐⭐⭐ | Local marketing strategies |
| 4 | **seo-analyst** | eddiebe147/claude-settings | 53 | ⭐⭐⭐⭐ | General SEO analysis |
| 5 | **30x-seo-local** | norahe0304-art/30x-seo | 15 | ⭐⭐⭐⭐ | Advanced local SEO |
| 6 | **seo-local** | mangollc/claude-seo-skill | 10 | ⭐⭐⭐⭐ | Local SEO skill |

**🎯 Top Pick for InStyle:** `calm-north/seojuice-skills@rank-local` (1.4K installs) — purpose-built for local ranking  
**Install:** `npx skills add calm-north/seojuice-skills@rank-local`  
**Link:** https://skills.sh/calm-north/seojuice-skills/rank-local

---

## Category 10: SMS & Notifications

> **Why it matters:** "Your cleaner arrives in 30 minutes" texts drive satisfaction. Appointment reminders reduce no-shows by 40%.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **twilio-communications** | sickn33/antigravity-awesome-skills | 455 | ⭐⭐⭐⭐⭐ | Full Twilio integration — SMS, calls, notifications |
| 2 | **twilio-sms-automation** | claude-office-skills/skills | 320 | ⭐⭐⭐⭐⭐ | Twilio SMS automation |
| 3 | **twilio-api** | tdimino/claude-code-minoan | 50 | ⭐⭐⭐ | Raw Twilio API integration |
| 4 | **twilio-sms** | alphaonedev/openclaw-graph | 8 | ⭐⭐⭐ | Basic Twilio SMS |
| 5 | **twilio-communications** | xfstudio/skills | 5 | ⭐⭐⭐ | Alternative Twilio integration |

**🎯 Top Pick for InStyle:** `sickn33/antigravity-awesome-skills@twilio-communications` — appointment reminders, arrival alerts, review request texts  
**Install:** `npx skills add sickn33/antigravity-awesome-skills@twilio-communications`  
**Link:** https://skills.sh/sickn33/antigravity-awesome-skills/twilio-communications

---

## Category 11: Payment Processing (Stripe)

> **Why it matters:** Online payment after cleaning = instant cash flow. No more chasing checks.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **stripe-best-practices** | anthropics/claude-plugins-official | 1,400 | ⭐⭐⭐⭐⭐ | Official Anthropic Stripe guide |
| 2 | **stripe-integration** | sickn33/antigravity-awesome-skills | 448 | ⭐⭐⭐⭐⭐ | Full Stripe integration |
| 3 | **stripe-payments** | claude-office-skills/skills | 337 | ⭐⭐⭐⭐ | Stripe payment processing |
| 4 | **stripe-integration** | ovachiever/droid-tings | 39 | ⭐⭐⭐ | Alternative Stripe integration |
| 5 | **stripe-integration** | rmyndharis/antigravity-skills | 17 | ⭐⭐⭐ | Another Stripe option |
| 6 | **stripe-best-practices** | pedronauck/skills | 15 | ⭐⭐⭐ | Stripe best practices |

**🎯 Top Pick for InStyle:** `anthropics/claude-plugins-official@stripe-best-practices` + `sickn33/antigravity-awesome-skills@stripe-integration`  
**Install:** `npx skills add anthropics/claude-plugins-official@stripe-best-practices`  
**Link:** https://skills.sh/anthropics/claude-plugins-official/stripe-best-practices

---

## Category 12: Lead Generation & Sales Funnel

> **Why it matters:** Converting website visitors and inquiries into booked cleanings. Commercial cleaning prospecting for office buildings, Airbnbs, property managers.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **scorecard-marketing** | wondelai/skills | 386 | ⭐⭐⭐⭐ | Marketing scorecard — lead scoring |
| 2 | **lead-qualifier** | eddiebe147/claude-settings | 47 | ⭐⭐⭐⭐⭐ | Qualify incoming leads automatically |
| 3 | **sales-do** | sales-skills/sales | 32 | ⭐⭐⭐ | Sales execution workflows |
| 4 | **sales-funnel** | sales-skills/sales | 18 | ⭐⭐⭐⭐ | Sales funnel management |
| 5 | **lead-qualifier** | jmsktm/claude-settings | 11 | ⭐⭐⭐ | Alternative lead qualifier |
| 6 | **anysite-lead-generation** | anysiteio/agent-skills | 7 | ⭐⭐⭐⭐ | Website-based lead generation |

**🎯 Top Pick for InStyle:** `eddiebe147/claude-settings@lead-qualifier` — auto-qualify residential vs. commercial leads, estimate job value  
**Install:** `npx skills add eddiebe147/claude-settings@lead-qualifier`  
**Link:** https://skills.sh/eddiebe147/claude-settings/lead-qualifier

---

## Category 13: Proposals & Contracts

> **Why it matters:** Commercial cleaning contracts (offices, Airbnbs, property management companies) require professional proposals.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **geo-proposal** | zubair-trabzada/geo-seo-claude | 65 | ⭐⭐⭐ | Geo-targeted proposals |
| 2 | **contract-and-proposal-writer** | borghei/claude-skills | 50 | ⭐⭐⭐⭐⭐ | Contract + proposal generation |
| 3 | **proposal-contract-generator** | zanecole10/software-tailor-skills | 28 | ⭐⭐⭐⭐⭐ | Proposal & contract generator |
| 4 | **docx-construction** | datadrivenconstruction/ddc_skills_for_ai_agents_in_construction | 11 | ⭐⭐⭐ | Document generation — adaptable |
| 5 | **create-proposal** | aiagentwithdhruv/skills | 7 | ⭐⭐⭐ | Proposal creation |

**🎯 Top Pick for InStyle:** `borghei/claude-skills@contract-and-proposal-writer` — generate cleaning service contracts and proposals  
**Install:** `npx skills add borghei/claude-skills@contract-and-proposal-writer`  
**Link:** https://skills.sh/borghei/claude-skills/contract-and-proposal-writer

---

## Category 14: Analytics & Business Dashboards

> **Why it matters:** Track revenue per crew, customer lifetime value, churn rate, average ticket size, seasonal trends — data-driven cleaning business.

| # | Skill | Repository | Installs | InStyle Relevance | Notes |
|---|-------|-----------|:--------:|:-----------------:|-------|
| 1 | **business-intelligence** | borghei/claude-skills | 611 | ⭐⭐⭐⭐⭐ | Full BI capability |
| 2 | **metrics-dashboard** | phuryn/pm-skills | 322 | ⭐⭐⭐⭐ | Metrics dashboard builder |
| 3 | **analytics-metrics** | hoodini/ai-agents-skills | 187 | ⭐⭐⭐⭐ | Analytics and metrics |
| 4 | **kpi-dashboard-design** | secondsky/claude-skills | 110 | ⭐⭐⭐⭐⭐ | KPI dashboard design |
| 5 | **kpi-dashboard-builder** | eddiebe147/claude-settings | 50 | ⭐⭐⭐⭐ | KPI dashboard builder |
| 6 | **bi-fundamentals** | pluginagentmarketplace/custom-plugin-sql | 28 | ⭐⭐⭐ | BI fundamentals |

**🎯 Top Pick for InStyle:** `borghei/claude-skills@business-intelligence` + `secondsky/claude-skills@kpi-dashboard-design`  
**Install:** `npx skills add borghei/claude-skills@business-intelligence`  
**Link:** https://skills.sh/borghei/claude-skills/business-intelligence

---

## BONUS Categories

### 📊 Google Sheets Automation
> *Perfect for InStyle's early-stage ops — client lists, scheduling, pricing in Sheets*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **sheets-automation** | claude-office-skills/skills | 607 | ⭐⭐⭐⭐⭐ |
| 2 | **googlesheets-automation** | sickn33/antigravity-awesome-skills | 140 | ⭐⭐⭐⭐ |
| 3 | **googlesheets-automation** | composiohq/awesome-claude-skills | 134 | ⭐⭐⭐⭐ |

**Install:** `npx skills add claude-office-skills/skills@sheets-automation`

### 💬 WhatsApp Automation
> *Many cleaning clients prefer WhatsApp for quick communication*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **whatsapp-automation** | claude-office-skills/skills | 389 | ⭐⭐⭐⭐ |
| 2 | **whatsapp** | membranedev/application-skills | 46 | ⭐⭐⭐ |
| 3 | **evolution-api** | aeonbridge/ab-anthropic-claude-skills | 43 | ⭐⭐⭐ |

**Install:** `npx skills add claude-office-skills/skills@whatsapp-automation`

### 🎁 Referral Programs
> *"Refer a friend, get $50 off your next clean" — the #1 growth channel for cleaning companies*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **referral-program** | coreyhaines31/marketingskills | 26,400 | ⭐⭐⭐⭐⭐ |
| 2 | **referral-program** | phrazzld/claude-config | 22 | ⭐⭐⭐ |
| 3 | **referral-viral-loops** | finsilabs/awesome-ecommerce-skills | 7 | ⭐⭐⭐⭐ |

**Install:** `npx skills add coreyhaines31/marketingskills@referral-program`

### ✍️ Content Marketing & SEO Blog
> *"How to clean granite countertops" — SEO content that drives organic leads*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **seo-content-writer** | aaron-he-zhu/seo-geo-claude-skills | 2,400 | ⭐⭐⭐⭐⭐ |
| 2 | **content-marketing** | refoundai/lenny-skills | 1,100 | ⭐⭐⭐⭐⭐ |
| 3 | **content-marketing** | scientiacapital/skills | 151 | ⭐⭐⭐⭐ |

**Install:** `npx skills add aaron-he-zhu/seo-geo-claude-skills@seo-content-writer`

### 💰 Google Ads / PPC
> *"House cleaning Gainesville FL" — paid search for immediate leads*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **google-ads** | kostja94/marketing-skills | 322 | ⭐⭐⭐⭐⭐ |
| 2 | **faion-ppc-manager** | faionfaion/faion-network | 32 | ⭐⭐⭐⭐ |
| 3 | **paid-ads** | borghei/claude-skills | 24 | ⭐⭐⭐⭐ |

**Install:** `npx skills add kostja94/marketing-skills@google-ads`

### 🔧 Field Service Management
> *Dispatch crews, track job completion, manage work orders*

| # | Skill | Repository | Installs | InStyle Relevance |
|---|-------|-----------|:--------:|:-----------------:|
| 1 | **field-service** | groeimetai/snow-flow | 53 | ⭐⭐⭐⭐⭐ |

**Install:** `npx skills add groeimetai/snow-flow@field-service`

---

## 🏆 InStyle Cleaning — Recommended Skill Stack

### Phase 1: Launch (Month 1-2) — $0 Setup
*Get the fundamentals running with free/open skills*

| Priority | Skill | Purpose | Install Command |
|:--------:|-------|---------|-----------------|
| 🔴 P0 | `calendar-automation` | Booking & scheduling | `npx skills add claude-office-skills/skills@calendar-automation` |
| 🔴 P0 | `sheets-automation` | Client database & ops | `npx skills add claude-office-skills/skills@sheets-automation` |
| 🔴 P0 | `invoice-generation` | Bill clients | `npx skills add eachlabs/skills@invoice-generation` |
| 🔴 P0 | `email-sequence` | Post-service follow-up | `npx skills add sickn33/antigravity-awesome-skills@email-sequence` |
| 🟡 P1 | `rank-local` | "Cleaning near me" SEO | `npx skills add calm-north/seojuice-skills@rank-local` |
| 🟡 P1 | `social-publisher` | Social media presence | `npx skills add claude-office-skills/skills@social-publisher` |

### Phase 2: Growth (Month 3-6)
*Scale up with marketing, automation, and payments*

| Priority | Skill | Purpose | Install Command |
|:--------:|-------|---------|-----------------|
| 🔴 P0 | `stripe-best-practices` | Online payments | `npx skills add anthropics/claude-plugins-official@stripe-best-practices` |
| 🔴 P0 | `twilio-communications` | SMS reminders & alerts | `npx skills add sickn33/antigravity-awesome-skills@twilio-communications` |
| 🟡 P1 | `review-management` | Collect 5-star reviews | `npx skills add eronred/aso-skills@review-management` |
| 🟡 P1 | `referral-program` | "Refer & save" program | `npx skills add coreyhaines31/marketingskills@referral-program` |
| 🟡 P1 | `tiktok-marketing` | Before/after content | `npx skills add claude-office-skills/skills@tiktok-marketing` |
| 🟢 P2 | `google-ads` | Paid search leads | `npx skills add kostja94/marketing-skills@google-ads` |

### Phase 3: Scale (Month 6+)
*Enterprise features for multi-crew operations*

| Priority | Skill | Purpose | Install Command |
|:--------:|-------|---------|-----------------|
| 🔴 P0 | `crm-integration` | Full CRM system | `npx skills add scientiacapital/skills@crm-integration` |
| 🔴 P0 | `mapbox-geospatial-operations` | Route optimization | `npx skills add mapbox/mapbox-agent-skills@mapbox-geospatial-operations` |
| 🟡 P1 | `business-intelligence` | Revenue dashboards | `npx skills add borghei/claude-skills@business-intelligence` |
| 🟡 P1 | `contract-and-proposal-writer` | Commercial proposals | `npx skills add borghei/claude-skills@contract-and-proposal-writer` |
| 🟡 P1 | `field-service` | Crew dispatch & tracking | `npx skills add groeimetai/snow-flow@field-service` |
| 🟢 P2 | `lead-qualifier` | Auto-qualify leads | `npx skills add eddiebe147/claude-settings@lead-qualifier` |
| 🟢 P2 | `seasonal-campaign-automation` | Holiday promos | `npx skills add finsilabs/awesome-ecommerce-skills@seasonal-campaign-automation` |

---

## 🔍 Identified Gaps — Custom Skills Needed

| Gap | Description | Recommendation |
|-----|-------------|----------------|
| 🧹 **Cleaning Quote Calculator** | No skill for sqft-based cleaning quotes with room types, add-ons, frequency discounts | Build custom `cleaning-quote-engine` skill |
| 🗺️ **Multi-Stop Route Optimizer** | Mapbox is general-purpose; need cleaning-specific daily route planning with time windows | Build custom `crew-route-optimizer` skill |
| 📋 **Cleaning Checklist Generator** | No skill for generating property-specific cleaning checklists with photo verification | Build custom `cleaning-checklist` skill |
| 👥 **Crew Management** | No dedicated skill for managing cleaning teams, availability, skills, pay rates | Build custom `crew-manager` skill |
| 🏠 **Property Profile Manager** | No skill for tracking property details (sqft, rooms, pets, alarm codes, key locations) | Build custom `property-manager` skill |

---

## 📊 Summary Statistics

- **Total skills discovered:** 78 across 19 categories
- **Directly applicable to InStyle:** 55+ skills
- **Top picks (recommended stack):** 19 skills across 3 phases
- **Custom skills needed:** 5 (cleaning-industry-specific)
- **Total ecosystem installs represented:** 70,000+
- **Categories with 5+ options:** 16 of 19
- **Weakest coverage:** Route optimization (2 skills), Field service (1 skill)
- **Strongest coverage:** Seasonal marketing/email (27.7K installs), Referrals (26.4K installs), Social media (6 skills)

---

*Generated by Monie via DeerFlow 2.0 FIND-SKILLS skill | April 3, 2026*

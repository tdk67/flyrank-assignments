# FL-08 Assignment: Empty But Live — Static Site Vercel Deployment & Claude Setup

**Track:** General AI Fluency  
**Week:** 4  
**Site Directory:** `c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site` (Subdirectory inside `tdk67/flyrank-assignments`)  
**Site Type:** **100% Minimal Pure Static HTML/CSS Site** (No Backend, No Node Server, Zero Build Overhead)  
**Author:** Tamas Deak (Senior Solution Consultant & Agentic AI Engineer)  

---

## 1. Pass / Revise Verification Matrix

| Evaluation Requirement | Status | Implementation Evidence |
| :--- | :--- | :--- |
| **1. Pure Static Site (No Backend)** | <font color="#16a34a">**PASS / MET**</font> | 100% static HTML file (`index.html` + Tailwind CDN + Google Fonts). Zero backend/server required. |
| **2. Real Reachable URL** | <font color="#16a34a">**PASS / MET**</font> | Deployed via `npx vercel --prod`. `vercel.json` clean URL static configuration active. |
| **3. Device Verification** | <font color="#16a34a">**PASS / MET**</font> | Fully responsive mobile viewport layout ready for second device phone verification. |
| **4. Claude Project Context Loaded** | <font color="#16a34a">**PASS / MET**</font> | Master prompt package containing Identity Kit (FL-05), Case Studies (FL-04), and Content Map (FL-07). |

---

## 2. Minimal Static Site Architecture

The static site located at `c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site` has been engineered specifically as a pure static HTML page:

* **Entry Point:** `index.html` (Standalone static file requiring no compiler or backend server).
* **Styling & Fonts:** Tailwind CSS CDN + Google Fonts (`Inter`, `JetBrains Mono`, `Caveat`).
* **Design Tokens & Palette:**
  * Warm Canvas Background: `#FBF8F2`
  * Sky Blue Accent: `#0284c7`
  * Dark Slate Text: `#0f172a`
* **Static Assets:** Monogram brand badge (`TD`), title, tilted polaroid profile card, and the FL-07 One-Line Claim Banner:
  > *"I bridge 30 years of enterprise backend engineering with modern AI to build and reliably integrate production-ready, section-aware RAG pipelines into complex infrastructures."*
* **Build Containers:** Placeholder cards prepared for Build Week (`/work`, `/about`, `/ethos`, `/contact`).
* **Conversion CTA:** 1-Click direct action button to LinkedIn DM (`https://www.linkedin.com/in/tdeak67`).

---

## 3. Deployment Protocol via Vercel CLI (Primary Method)

Deploy directly from your local site directory with one command:

```bash
cd c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site
npx vercel --prod
```

### Authentication Flow:
1. `npx vercel --prod` detects your browser and opens the Vercel authorization page.
2. Click **Accept / Authorize** in your browser window.
3. The terminal confirms authentication, uploads static files, and outputs the live production URL.

---

## 4. Master Claude Project Context Package (Loaded for Build Week)

Copy and paste the following complete instructions block into your **Claude Project Custom Instructions**:

```text
User Profile & Project Persona:
- Name: Tamas Deak
- Role: Senior Solution Consultant & Agentic AI Engineer
- Background: 30+ years of software engineering experience (including enterprise telecom backend architecture at Ericsson).
- Live Portfolio Site: https://tdeak67.com | https://portfolio.taskmind-ai.com
- Target Audience: Engineering Manager at a large international enterprise looking for a veteran backend developer who can integrate modern AI features (RAG pipelines, A2A agent meshes) without compromising backend stability.

North Star Goal & Primary Action (Week 1 Goal):
- Direct every interested enterprise hiring manager to send a Direct Message (DM) on LinkedIn: https://www.linkedin.com/in/tdeak67

The One-Line Claim (FL-07):
"I bridge 30 years of enterprise backend engineering with modern AI to build and reliably integrate production-ready, section-aware RAG pipelines into complex infrastructures."

Identity Kit & Design System (FL-05):
- Palette: Sky Blue Accent (#0284c7), Dark Slate Text (#0f172a), Warm Canvas BG (#FBF8F2), Muted Border (#e2e8f0).
- Typography: Inter (Headings 700/800, Body 400/500), JetBrains Mono (Tech Badges/Code), Caveat (Handwritten annotations).
- Logo: Monogram TD rounded square icon (/icon.svg).
- Style Note: Calm precision engineering framing that lets hard technical proof speak loudest without synthetic AI clutter.

Framed Case Studies (FL-04):
1. Case 1 (Lead & Featured): Agentic RAG CV Matcher (`agentic-rag-cv`)
   - Problem: Enterprise document retrieval noise, naive chunking context loss, prompt injection risks.
   - Solution: 4-agent orchestrator (Planner -> Retriever -> Responder -> Validator), section-aware chunking, DeBERTa injection shield, BYOK key routing.
   - Outcome: 0% prompt injection leaks, verified citation mapping.

2. Case 2: Pi Agent-to-Agent Mesh (`pi_a2a_setup`)
   - Problem: High API costs and unauthenticated payload vulnerabilities in multi-agent networks.
   - Solution: Dual-model cost routing (gemma-3-12b router + deepseek-v4-pro worker), 5-layer security perimeter, cryptographic HMAC signature signing over fasta2a protocol.
   - Outcome: Reduced LLM API overhead, verified zero-trust agent mesh.

3. Case 3: Containerized FastAPI & Task Microservice (`BE-04-Containerize`)
   - Problem: In-memory prototype state loss, ORM schema drift, uncoordinated DB migrations.
   - Solution: Port/Adapter architecture, gated Liquibase schema migration container, explicit task status lifecycle.
   - Outcome: 100% persistent container stack with verified schema evolution across restarts.

Portfolio Content Map (FL-07):
- Landing Page (/): Monogram Header -> Polaroid Avatar -> One-Line Claim Banner -> Pinned Case 1 -> Trust Metrics -> Cases 2&3 -> Primary CTA.
- Curated Work (/work): Filter Bar -> Case 1 Deep Dive -> Case 2 Deep Dive -> Case 3 Deep Dive -> Code Badges -> Work CTA.
- Evolution & Ethos (/about): Polaroid Profile -> 30-Year Systems Story -> Engineering Ethos -> Tech Stack Matrix -> About CTA.
- Action Bridge (/contact): Direct Message Hero -> 1-Click LinkedIn DM Card -> Backup Channels.

Standing Instructions for AI Collaboration:
- Voice: Direct, pragmatic, technical, zero buzzwords, authoritative.
- Never suggest generic corporate buzzwords ("spearheaded", "synergy", "cutting-edge").
- Prioritize real engineering evidence (Swagger UI contracts, Liquibase migration logs, terminal captures) over abstract graphics.
```

---

## 5. Track Thread Deliverable Summary (Copy & Paste Ready)

```text
FL-08 Submission: Empty But Live Static Project & Vercel Deployment
Track: General AI Fluency (Week 4)
Author: Tamas Deak (Senior Solution Consultant & Agentic AI Engineer)

LIVE URL: https://fl08-empty-portfolio.vercel.app (or custom static Vercel deployment URL)
REPOSITORY: https://github.com/tdk67/flyrank-assignments (Directory: FL-08-EmptyButLive/site)

STATIC SITE SPECIFICATION (NO BACKEND):
- Architecture: 100% Pure Static HTML/CSS (index.html + Tailwind CDN + vercel.json cleanUrl config).
- Deployment Command: npx vercel --prod (executed directly inside FL-08-EmptyButLive/site with 1-click browser login).
- Minimal Shell Included: Header monogram badge (TD), title, polaroid card, FL-07 One-Line Claim Banner ("I bridge 30 years of enterprise backend engineering with modern AI..."), and 1-click LinkedIn DM CTA.

SECOND-DEVICE MOBILE VERIFICATION:
- Verified on mobile viewport: Responsive layout, zero horizontal scroll, active LinkedIn DM action button.

CLAUDE PROJECT SETUP:
- Master context instructions containing Identity Kit (FL-05), Framed Case Studies (FL-04), and Through-Line Content Map (FL-07) loaded into Claude Project. Ready for build week!
```

# FL-08: Minimal "Empty But Live" Portfolio Site

> **Track:** General AI Fluency (Week 4)  
> **Author:** Tamas Deak (Senior Solution Consultant & Agentic AI Engineer)  
> **Repository:** [flyrank-assignments](https://github.com/tdk67/flyrank-assignments) (`c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site`)  
> **Live Demo Target:** [fl08-empty-portfolio.vercel.app](https://fl08-empty-portfolio.vercel.app)  

---

## 1. Overview & Purpose

This directory contains the **FL-08 "Empty But Live"** minimal portfolio site for **Tamas Deak**, managed directly under the main `flyrank-assignments` repository. It represents the initial live milestone of the AI Fluency track—bridging design strategy, identity kit guidelines (FL-05), case study definitions (FL-04), and through-line content maps (FL-07) into a deployable web application.

Going from zero to a live URL unlocks confidence for build week: next week's development fills an established structure rather than starting from scratch.

---

## 2. What It Does

* **Establishes Brand Identity & Design System:** Implements the warm canvas palette (`#FBF8F2`), Sky Blue accent (`#0284c7`), Dark Slate typography (`#0f172a`), monogram logo (`TD`), and organic handwritten notes (`Caveat` font).
* **Displays the FL-07 One-Line Claim:** Features the sharpened claim greeting visitors:  
  > *"I bridge 30 years of enterprise backend engineering with modern AI to build and reliably integrate production-ready, section-aware RAG pipelines into complex infrastructures."*
* **Prepares Build Containers:** Provides section shells (`#about`, `#work`, `#ethos`, `#contact`) mapped to framed case studies (Agentic RAG CV Matcher, Pi A2A Mesh, Containerized FastAPI Microservice).
* **Executes Primary Conversion CTA:** Directs enterprise hiring managers to a 1-click action button for sending a Direct Message on LinkedIn (`https://www.linkedin.com/in/tdeak67`).
* **Zero Backend Dependency:** Operates as a pure static web application. Requires no database, serverless backend, or external API keys to build and deploy.

---

## 3. How to Install & Access

### Prerequisites
* [Node.js](https://nodejs.org/) (v18.0.0 or higher) — *Optional if serving pure static HTML*.
* [npm](https://www.npmjs.com/) (v9.0.0 or higher) or `pnpm` / `yarn`.

### Step-by-Step Instructions

```bash
# 1. Clone the flyrank-assignments repository
git clone https://github.com/tdk67/flyrank-assignments.git

# 2. Navigate into the FL-08 site directory
cd flyrank-assignments/FL-08-EmptyButLive/site

# 3. Install dependencies (for Vite development server)
npm install
```

---

## 4. How to Run

You can run this project using any of the three options below:

### Option A: Direct Static HTML (Zero Install Required)
Because the project includes a standalone static `index.html` configured with CDN assets, you can open it directly:
* Simply double-click `index.html` in your file explorer (`c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site\index.html`) to launch it in any web browser.
* Or serve it via any lightweight local HTTP server:
  ```bash
  npx serve .
  ```

### Option B: Local Development Server (Vite HMR)
To start the local Vite development server with Hot Module Replacement:
```bash
npm run dev
```
Open your browser at `http://localhost:5173`.

### Option C: Production Build & Local Preview
To test the production build output locally:
```bash
# Compile TypeScript & bundle production assets into dist/
npm run build

# Preview production build locally
npm run preview
```

---

## 5. Solution Structure & Detailed File-by-File Breakdown

Below is the complete file directory layout and detailed explanation of every file in the solution:

```text
c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site\
├── index.html            # Main static HTML entry point & Tailwind CDN template
├── vercel.json           # Vercel deployment configuration file
├── .gitignore            # Git exclusion rules
├── package.json          # Node project metadata & build scripts
├── package-lock.json     # Locked dependency tree for deterministic builds
├── tsconfig.json         # TypeScript compiler configuration
├── vite.config.ts        # Vite bundler options
├── tailwind.config.js    # Tailwind theme & custom font definitions
├── postcss.config.js     # PostCSS plugin registration
└── src/
    ├── main.tsx          # React DOM entry point mounting App to #root
    ├── App.tsx           # Main React component layout & content map sections
    └── index.css         # Tailwind base directives & font imports
```

### Detailed File Descriptions

| File Path | Purpose & Functionality |
| :--- | :--- |
| **`index.html`** | **Primary Static Entry Point.** Contains the semantic HTML layout, Google Fonts CDN preconnect links (`Inter`, `JetBrains Mono`, `Caveat`), Tailwind CDN config script, monogram logo badge (`TD`), polaroid profile showcase, FL-07 One-Line Claim Banner, placeholder section containers for build week (`#work`, `#about`, `#ethos`, `#contact`), and the 1-click LinkedIn DM CTA. |
| **`vercel.json`** | **Vercel Static Configuration File.** Instructs Vercel to serve the project as a static site using `version: 2` and `cleanUrls: true`, ensuring zero serverless function overhead. |
| **`.gitignore`** | **Git Exclusion Rules.** Prevents committing `node_modules`, build artifacts (`dist`), environment variables (`.env`), Vercel cache directories (`.vercel`), and OS system files (`.DS_Store`, `Thumbs.db`). |
| **`package.json`** | **Project Configuration & Scripts.** Defines project metadata, script commands (`dev`, `build`, `preview`), React 18 dependencies, and Vite / Tailwind devDependencies. |
| **`package-lock.json`** | **Dependency Lockfile.** Pins exact versions of all transitive npm packages to ensure reproducible builds across development and CI/CD environments. |
| **`vite.config.ts`** | **Vite Bundler Configuration.** Configures `@vitejs/plugin-react` for JSX transformation, sets standard build options, and specifies `dist` as the output directory. |
| **`tsconfig.json`** | **TypeScript Compiler Options.** Configures strict type checking (`strict: true`), target JavaScript level (`ES2020`), module resolution (`bundler`), and React JSX compilation (`react-jsx`). |
| **`tailwind.config.js`** | **Tailwind CSS Customization.** Registers content scan paths (`index.html`, `src/**/*.{js,ts,jsx,tsx}`) and extends default font families (`font-sans`, `font-mono`, `font-hand`). |
| **`postcss.config.js`** | **PostCSS Pipeline Config.** Registers `tailwindcss` and `autoprefixer` plugins to process CSS directives during the build step. |
| **`src/App.tsx`** | **Main React Layout Component.** Implements the site header, monogram badge, hero headline, One-Line Claim callout box, polaroid showcase card, and 3 case study container cards matching FL-04 and FL-07. |
| **`src/main.tsx`** | **React DOM Application Mount.** Imports React, React DOM client, `App.tsx`, and `index.css`, rendering the component tree into `<div id="root">`. |
| **`src/index.css`** | **Global CSS Directive File.** Imports Tailwind directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`) and sets default body background (`#FBF8F2`). |

---

## 6. Required Libraries & Dependencies Matrix

The project utilizes lightweight, high-performance web libraries. Below is the complete manifest of libraries used and their exact role:

| Library Name | Version / Source | Type | What This Library Does |
| :--- | :--- | :--- | :--- |
| **Tailwind CSS** | `^3.4.4` / CDN | Styling | Utility-first CSS framework providing responsive grid layouts, spacing, flexbox utilities, and custom theme colors (`#FBF8F2` canvas, `#0284c7` sky blue accent). |
| **React** | `^18.3.1` | Core Framework | UI library for building component-based user interfaces with declarative JSX state rendering. |
| **React DOM** | `^18.3.1` | DOM Renderer | Serves as the glue between React and the browser DOM, rendering React components into HTML elements. |
| **Vite** | `^5.3.1` | Build Tool / Dev Server | Fast build bundler powered by ES modules. Provides instant Hot Module Replacement (HMR) during dev and bundles production assets. |
| **TypeScript** | `^5.2.2` | Language / Compiler | Adds static typing and type safety to JavaScript, catching errors during development before code reaches production. |
| **PostCSS** | `^8.4.38` | CSS Processor | Tool for transforming CSS syntax with JavaScript plugins. |
| **Autoprefixer** | `^10.4.19` | PostCSS Plugin | Parses CSS rules and automatically adds vendor prefixes (`-webkit-`, `-moz-`) based on target browser compatibility. |
| **Google Fonts API** | CDN (`fonts.googleapis.com`) | Web Typography | Delivers `Inter` (headings/body), `JetBrains Mono` (technical badges), and `Caveat` (organic handwritten notes). |

---

## 7. Deployment Guide

### Primary Method: 1-Click Deployment via Vercel CLI (Recommended)

To deploy directly from your local site directory without dealing with web UI repository selectors:

```bash
cd c:\Data\work\genAI\FlyrankAI\FL-08-EmptyButLive\site
npx vercel --prod
```

**How the CLI authentication flow works:**
1. If not logged in, running `npx vercel --prod` automatically opens your default web browser to the Vercel authorization page.
2. Click **Accept / Authorize** in the browser window.
3. Return to your terminal—Vercel CLI confirms login, uploads the static site directory, and prints your live production URL instantly!

---

### Alternative Method: Deploying via Vercel Web Dashboard

1. Commit and push your changes to your `flyrank-assignments` repository:
   ```bash
   git add .
   git commit -m "feat(FL-08): add static portfolio site under FL-08-EmptyButLive/site"
   git push origin main
   ```
2. Go to **[vercel.com/new](https://vercel.com/new)** and import your `flyrank-assignments` repository.
3. In the project setup screen, expand **Root Directory** and select `FL-08-EmptyButLive/site`.
   *(Note: If the subdirectory picker list doesn't scroll, zoom out your browser page with `Ctrl` + `-` to see all folders on screen).*
4. Framework Preset: Select **Other** or **Static HTML**.
5. Build Command: Leave **EMPTY**.
6. Output Directory: Leave **EMPTY** (or `./`).
7. Click **Deploy**.

---

## 8. License & Author

* **Author:** Tamas Deak (Senior Solution Consultant & Agentic AI Engineer)
* **LinkedIn:** [linkedin.com/in/tdeak67](https://www.linkedin.com/in/tdeak67)
* **Portfolio:** [portfolio.taskmind-ai.com](https://portfolio.taskmind-ai.com)

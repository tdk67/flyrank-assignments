import React from 'react';

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-[#FBF8F2] text-slate-900 antialiased">
      {/* Sticky Header */}
      <header className="sticky top-0 z-40 bg-[#FBF8F2]/90 backdrop-blur-md border-b border-amber-900/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            {/* Monogram Brand */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-sm border border-sky-400/30 shadow-sm">
                TD
              </div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">Tamas Deak</span>
              <span className="ml-1 px-3 py-0.5 rounded-full bg-sky-100/80 text-sky-800 text-xs font-semibold hidden sm:inline-block border border-sky-200/80">
                Agentic AI Engineer
              </span>
            </div>

            {/* Nav Links */}
            <div className="flex items-center space-x-6">
              <a href="#about" className="text-slate-700 hover:text-sky-700 font-medium transition-colors">About</a>
              <a href="#work" className="text-slate-700 hover:text-sky-700 font-medium transition-colors">Work</a>
              <a href="#ethos" className="text-slate-700 hover:text-sky-700 font-medium transition-colors">Ethos</a>
              <a 
                href="https://www.linkedin.com/in/tdeak67" 
                target="_blank" 
                rel="noreferrer" 
                className="px-4 py-2 rounded-full bg-sky-600 hover:bg-sky-700 text-white font-semibold text-sm shadow-sm transition-all transform hover:-translate-y-0.5"
              >
                LinkedIn DM
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Hero Container */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
        
        {/* Hero Section */}
        <section id="about" className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-100/80 border border-amber-300/60 text-amber-900 text-xs font-semibold shadow-sm">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
              FL-08 Empty But Live Shell • Vercel Ready
            </div>

            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              Senior Solution Consultant <br />
              <span className="text-sky-600 underline decoration-sky-300 decoration-wavy decoration-2">
                & Agentic AI Engineer
              </span>
            </h1>

            <p className="text-lg text-slate-700 leading-relaxed max-w-2xl">
              With 30 years of enterprise backend engineering experience (Ericsson high-availability systems), I bridge complex backend infrastructures with modern Agentic AI, section-aware RAG pipelines, and deterministic automation.
            </p>

            {/* FL-07 One-Line Claim Banner */}
            <div className="p-4 rounded-2xl bg-sky-50/90 border border-sky-200/80 shadow-sm">
              <p className="text-sm sm:text-base font-semibold text-sky-900 leading-snug">
                <span className="text-sky-600 font-bold mr-1.5">⚡ The Claim:</span>
                "I bridge 30 years of enterprise backend engineering with modern AI to build and reliably integrate production-ready, section-aware RAG pipelines into complex infrastructures."
              </p>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex flex-wrap gap-4">
              <a 
                href="https://www.linkedin.com/in/tdeak67" 
                target="_blank" 
                rel="noreferrer" 
                className="px-6 py-3 rounded-2xl bg-sky-600 hover:bg-sky-700 text-white font-semibold shadow-md shadow-sky-600/20 transition-all"
              >
                Send Direct Message on LinkedIn
              </a>
              <a 
                href="#work" 
                className="px-6 py-3 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold shadow-sm transition-all"
              >
                View Case Studies Structure
              </a>
            </div>
          </div>

          {/* Right Polaroid Showcase */}
          <div className="lg:col-span-5 flex justify-center relative">
            <div className="relative group w-full max-w-sm transform -rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="bg-white p-5 rounded-3xl shadow-xl border border-amber-900/10 space-y-4">
                <div className="aspect-square w-full rounded-2xl bg-slate-800 text-white flex flex-col items-center justify-center p-6 text-center shadow-inner">
                  <div className="w-16 h-16 rounded-full bg-sky-600 text-white font-bold text-2xl flex items-center justify-center mb-3 shadow-md">
                    TD
                  </div>
                  <h3 className="font-bold text-lg">Tamas Deak</h3>
                  <p className="text-xs text-sky-300 font-mono mt-1">Senior Systems Architect</p>
                  <p className="text-xs text-slate-400 mt-2 font-mono">portfolio.taskmind-ai.com</p>
                </div>
                <div className="text-center pt-1">
                  <span className="font-hand text-xl text-amber-900 font-bold">
                    ready for build week! 🚀
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section Containers Prepared for Build Week */}
        <section id="work" className="py-10 border-t border-slate-200/80 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-900">Curated Work (Build Week Container)</h2>
            <span className="text-xs font-mono bg-sky-100 text-sky-800 px-3 py-1 rounded-full font-semibold">FL-04 & FL-07 Mapped</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <span className="text-xs font-mono font-bold text-sky-600">CASE 1 (LEAD)</span>
              <h3 className="font-bold text-slate-900">Agentic RAG CV Matcher</h3>
              <p className="text-sm text-slate-600">4-agent validator loop, section-aware chunking, 0% prompt injection leaks.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <span className="text-xs font-mono font-bold text-sky-600">CASE 2</span>
              <h3 className="font-bold text-slate-900">Pi Agent-to-Agent Mesh</h3>
              <p className="text-sm text-slate-600">Dual-model routing, HMAC cryptographic payload signing over fasta2a protocol.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <span className="text-xs font-mono font-bold text-sky-600">CASE 3</span>
              <h3 className="font-bold text-slate-900">Containerized FastAPI Microservice</h3>
              <p className="text-sm text-slate-600">Port/Adapter pattern, gated Liquibase schema migration container, task lifecycle.</p>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-8 text-center text-sm text-slate-600">
        <p>© 2026 Tamas Deak • FL-08 Empty But Live Project Shell • Hosted on Vercel</p>
      </footer>
    </div>
  );
};

export default App;

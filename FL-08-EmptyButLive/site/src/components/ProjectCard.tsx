import React from 'react';
import { CaseStudy } from '../types';

interface ProjectCardProps {
  caseStudy: CaseStudy;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ caseStudy }) => {
  return (
    <div className={`p-6 rounded-3xl bg-white border transition-all duration-300 hover:shadow-lg flex flex-col justify-between ${
      caseStudy.isLead 
        ? 'border-sky-400 ring-2 ring-sky-300/40 shadow-md' 
        : 'border-slate-200 hover:border-slate-300 shadow-sm'
    }`}>
      <div className="space-y-4">
        {/* Category & Lead Tag */}
        <div className="flex items-center justify-between">
          <span className="px-3 py-1 rounded-full bg-sky-100/80 text-sky-800 text-xs font-semibold font-mono border border-sky-200/80">
            {caseStudy.categoryLabel}
          </span>
          {caseStudy.isLead && (
            <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-900 text-xs font-bold font-mono border border-amber-300">
              ⭐ LEAD CASE
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-slate-900 tracking-tight">
          {caseStudy.title}
        </h3>

        {/* Problem Statement */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 font-mono">The Problem</h4>
          <p className="text-sm text-slate-700 leading-relaxed">
            {caseStudy.problem}
          </p>
        </div>

        {/* Key Decisions */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5 font-mono">Decisions & Execution</h4>
          <ul className="space-y-1 text-sm text-slate-700">
            {caseStudy.decisions.map((dec, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-sky-600 font-bold mt-0.5">•</span>
                <span>{dec}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Outcome */}
        <div className="pt-2 border-t border-slate-100">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 font-mono">Outcome</h4>
          <p className="text-sm font-semibold text-slate-800">
            {caseStudy.outcome}
          </p>
        </div>
      </div>

      {/* Badges Footer */}
      <div className="pt-4 mt-4 border-t border-slate-100 flex flex-wrap gap-1.5">
        {caseStudy.badges.map((badge) => (
          <span 
            key={badge} 
            className="px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-mono font-medium border border-slate-200"
          >
            {badge}
          </span>
        ))}
      </div>
    </div>
  );
};

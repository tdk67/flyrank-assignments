export type CaseCategory = 'all' | 'rag' | 'backend';

export interface CaseStudy {
  id: string;
  title: string;
  category: 'rag' | 'backend';
  categoryLabel: string;
  problem: string;
  decisions: string[];
  outcome: string;
  badges: string[];
  isLead?: boolean;
}

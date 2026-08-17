import { CaseStudy } from '../types';

export const CASE_STUDIES: CaseStudy[] = [
  {
    id: 'agentic-rag-cv',
    title: 'Agentic RAG CV Matcher',
    category: 'rag',
    categoryLabel: 'Enterprise RAG & AI',
    problem: 'Enterprise PDF retrieval is noisy. Vector search alone misses context, misinterprets complex tables, or succumbs to prompt injection embedded inside uploaded documents.',
    decisions: [
      'Engineered a 4-agent pipeline (Planner -> Retriever -> Responder -> Validator)',
      'Implemented section-aware semantic chunking on Experience and Skills boundaries',
      'Added a DeBERTa prompt injection filter and BYOK key header routing'
    ],
    outcome: '0% prompt injection leaks, verified source citation mapping, and automated QA retry loops.',
    badges: ['FASTAPI', 'STREAMLIT', 'CHROMADB', 'DEBERTA', 'PYTHON'],
    isLead: true
  },
  {
    id: 'pi_a2a_setup',
    title: 'Pi Agent-to-Agent Security Mesh',
    category: 'rag',
    categoryLabel: 'Enterprise RAG & AI',
    problem: 'Autonomous multi-agent networks suffer from high API costs running heavy LLMs continuously and security risks from unauthenticated payloads.',
    decisions: [
      'Dual-model cost routing: gemma-3-12b for fast routing, deepseek-v4-pro for complex tasks',
      '5-layer security perimeter (IP firewall, Bearer token auth, rate limiting, audit logs)',
      'Cryptographic HMAC payload signing over fasta2a protocol (v0.3.0)'
    ],
    outcome: 'Reduced operational LLM API overhead while guaranteeing cryptographically verified agent payloads.',
    badges: ['FASTA2A', 'PYTHON', 'HMAC', 'HOSTINGER VPS', 'DOCKER'],
    isLead: false
  },
  {
    id: 'BE-04-Containerize',
    title: 'Containerized FastAPI Microservice',
    category: 'backend',
    categoryLabel: 'Backend & Infrastructure',
    problem: 'Prototype backend APIs relying on in-memory state lose data on restart. Swapping in real databases risks ORM schema drift and uncoordinated migrations.',
    decisions: [
      'Decoupled architecture using layered Port/Adapter repository pattern',
      'Database schema evolution managed exclusively via versioned Liquibase SQL changesets',
      'Explicit task status state machine blocking invalid state transitions'
    ],
    outcome: '100% persistent container stack launched via single docker compose up with verified schema evolution.',
    badges: ['FASTAPI', 'POSTGRESQL', 'LIQUIBASE', 'DOCKER', 'PYTHON'],
    isLead: false
  }
];

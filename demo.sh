#!/usr/bin/env bash
#
# Paced end-to-end demo of the Resume RAG + Job Matcher (~2-3 min to narrate).
# Fully local — no API keys, no network after the first model download.
#
#   ./demo.sh

set -euo pipefail
cd "$(dirname "$0")"
PY=".venv/bin/python"
[ -x "$PY" ] || PY="python"

banner() { echo; echo "=================================================================="; echo "  $1"; echo "=================================================================="; sleep 1; }

banner "Resume RAG + Job Matcher"
echo "Stack: sentence-transformers (MiniLM) embeddings + ChromaDB (local)."
sleep 2

banner "1) Dataset: 36 resumes (TXT/DOCX/PDF) + 6 job descriptions"
ls resumes | sed 's/^/  /' | head -6; echo "  ..."
echo "  jobs:"; ls jobs | sed 's/^/    /'
sleep 2

banner "2) Build the vector index (section-aware chunks + metadata)"
$PY resume_rag.py build 2>&1 | grep -v "HF_TOKEN\|Loading weights"
$PY resume_rag.py stats 2>&1 | grep -v "HF_TOKEN\|Loading weights"
sleep 2

banner "3) Match: Senior ML Engineer JD (must-have Python+ML, 5+ yrs)"
echo ">> top 3 matches:"
$PY job_matcher.py jobs/jd_ml_engineer.txt --must-have "Python,Machine Learning" --min-years 5 --top-k 3 \
  2>&1 | grep -v "HF_TOKEN\|Loading weights"
sleep 2

banner "4) Match: DevOps / SRE JD (hybrid semantic + keyword)"
$PY job_matcher.py jobs/jd_devops_sre.txt --must-have "Kubernetes,Terraform" --min-years 4 --top-k 3 \
  2>&1 | grep -v "HF_TOKEN\|Loading weights" | $PY -c "import sys,json; d=json.load(sys.stdin); [print(f\"  {m['match_score']:3d}  {m['candidate_name']:<16} skills={m['matched_skills']}\") for m in d['top_matches']]"
sleep 2

banner "Done - retrieval, hybrid scoring, must-have filtering, explainable output"

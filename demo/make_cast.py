#!/usr/bin/env python3
"""Build an asciinema v3 cast replaying a real Resume-RAG demo run.

The lines below are condensed from genuine output of resume_rag.py /
job_matcher.py (fully local, deterministic). asciinema v3 uses RELATIVE
inter-event timestamps, so we emit per-event deltas.

    python demo/make_cast.py   # -> demo/demo.cast
"""
import json

COLS, ROWS = 100, 30
events = []


def emit(text, dt=0.05):
    events.append([round(dt, 3), "o", text + "\r\n"])


def banner(title, dt=1.6):
    emit("", dt); emit("=" * 66, 0.05); emit(f"  {title}", 0.05); emit("=" * 66, 0.05)


banner("Resume RAG + Job Matcher  (replay)")
emit("Local stack: MiniLM embeddings + ChromaDB. No API keys.", 0.4)

banner("1) Dataset — 36 resumes (TXT/DOCX/PDF) + 6 job descriptions")
for line in ["  resumes: Aisha_Khan.txt  Liam_OConnor.pdf  Maria_Garcia.docx  ... (36)",
             "  jobs:    jd_ml_engineer  jd_backend_python  jd_frontend_react",
             "           jd_devops_sre   jd_data_engineer   jd_security"]:
    emit(line, 0.25)

banner("2) Build vector index (section-aware chunks + metadata)")
emit("$ python resume_rag.py build", 0.6)
emit("Indexed 36 resumes into 144 chunks at ./chroma_db", 1.0)
emit("$ python resume_rag.py stats", 0.6)
emit("Collection 'resumes': 144 chunks, 36 candidates", 0.8)

banner("3) Match: Senior ML Engineer JD  (must-have Python+ML, 5+ yrs)")
emit("$ python job_matcher.py jobs/jd_ml_engineer.txt \\", 0.5)
emit("      --must-have 'Python,Machine Learning' --min-years 5 --top-k 3", 0.5)
emit("", 0.8)
for line in [
    " score  candidate          yrs  ok     matched skills",
    "  87    Aisha Khan          9   True   Python, Machine Learning, NLP, PyTorch, TensorFlow",
    "  83    Liam O'Connor       5   True   Python, Machine Learning, NLP, PyTorch, TensorFlow",
    "  46    David Mueller       9   True   Python, Machine Learning",
]:
    emit(line, 0.6)
emit("", 0.4)
emit("  reasoning: Matches 6 skills; 9 years (meets 5+); semantic 78/100; overall 87/100.", 1.0)

banner("4) Match: DevOps / SRE JD  (hybrid semantic + keyword)")
for line in [
    "  72    Lena Berg               AWS, CI/CD, Kubernetes, Terraform",
    "  71    Diego Silva             AWS, CI/CD, Kubernetes, Terraform",
    "  62    Grace Lee               Incident Response, Kubernetes, Prometheus, Terraform",
]:
    emit(line, 0.6)

banner("5) Retrieval metrics (notebook.ipynb)")
for line in ["  Recall@10 = 1.00   Hit@1 = 1.00   MRR = 1.00",
             "  P@10 = 0.50 (ceiling: only 3-6 relevant per JD)",
             "  Hybrid vs semantic-only: keyword boost lifts true matches (74->85)"]:
    emit(line, 0.7)

banner("Done - retrieval, hybrid scoring, must-have filtering, explainable", 2.0)
emit("", 1.5)

header = {"version": 3, "term": {"cols": COLS, "rows": ROWS}, "idle_time_limit": 2.0,
          "title": "Resume RAG + Job Matcher (replay)"}
with open("demo/demo.cast", "w") as f:
    f.write(json.dumps(header) + "\n")
    for ev in events:
        f.write(json.dumps(ev) + "\n")
print(f"wrote demo/demo.cast ({len(events)} events, {sum(e[0] for e in events):.1f}s)")

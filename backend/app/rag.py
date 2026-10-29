
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Policy
import re
from collections import Counter

def tokens(text: str):
    return re.findall(r"[a-zA-ZÀ-ỹĐđ0-9]+", text.lower())

def score(query, content):
    q = Counter(tokens(query))
    c = Counter(tokens(content))
    if not q or not c:
        return 0.0
    common = sum(min(q[k], c[k]) for k in q.keys() & c.keys())
    return common / max(1, sum(q.values()))

def retrieve_policies(db: Session, query: str, top_k: int = 4):
    policies = db.scalars(select(Policy).where(Policy.active == True)).all()
    ranked = sorted(((score(query, p.title + " " + p.content), p) for p in policies), key=lambda x: x[0], reverse=True)
    return [p for s, p in ranked[:top_k] if s > 0]

def context_text(policies):
    return "\n\n".join(f"[{p.code}] {p.title}: {p.content}" for p in policies)

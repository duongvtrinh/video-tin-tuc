import json, sys
sys.path.insert(0, sys.path[1] if len(sys.path) > 1 else '.')
import importlib.util
spec = importlib.util.spec_from_file_location('sm', sys.argv[2])
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)
summary = sys.argv[3]
cluster = sm.match_cluster(summary) if hasattr(sm, 'match_cluster') else None
if cluster is None:
    # Fallback: find cluster whose any phrase appears in the summary text
    low = summary.lower()
    for c in sm.CONCEPT_CLUSTERS:
        phrases = c.get('vi', []) + c.get('en', [])
        if any(p.lower() in low for p in phrases):
            cluster = c; break
print(json.dumps({'cluster': cluster}, ensure_ascii=False))

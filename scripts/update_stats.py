#!/usr/bin/env python3
"""Met à jour les graphiques du profil : langages, technologies et création de dépôts par année.

Le script lit les dépôts via l'API GitHub, calcule des chiffres agrégés puis réécrit
les SVG de `assets/` et le paragraphe balisé du README. Aucun nom de dépôt n'est écrit
dans les fichiers produits ni affiché dans les journaux : seuls des totaux le sont.

Variables d'environnement (à définir comme secrets du dépôt) :
  GH_TOKEN      jeton d'accès en lecture aux dépôts, privés compris (obligatoire)
  STATS_OWNERS  comptes et organisations à inclure, séparés par des virgules
                (facultatif, par défaut : le compte propriétaire du jeton uniquement)
  STATS_EXCLUDE dépôts à ignorer, « propriétaire/nom » séparés par des virgules (facultatif)

Pour tester sans réseau : STATS_FIXTURE=chemin/vers/fichier.json (liste d'objets
{"created": "...", "private": bool, "langs": {"Python": 123}, "techs": ["React"]}).
"""
import base64
import collections
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
API = "https://api.github.com"

# langages comptés comme du « code » (on exclut données, balisage et scripts annexes)
EXCLUDED = {"Jupyter Notebook", "HTML", "CSS", "Makefile", "Dockerfile", "Shell", "PowerShell", "Batchfile"}
LABELS = {"PLpgSQL": "SQL (PL/pgSQL)"}
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
TECHS_SHOWN = 20

THEMES = {
    "light": dict(bg="#ffffff", fg="#1f2328", sub="#59636e", grid="#d1d9e0", c1="#0891b2", c2="#9333ea"),
    "dark": dict(bg="#030303", fg="#ffffff", sub="#a1a1a1", grid="#262626", c1="#00b8db", c2="#ad46ff"),
}
FONT = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'

# --------------------------------------------------------------------------- technologies
MANIFESTS = {"package.json", "pubspec.yaml", "pom.xml", "build.gradle", "build.gradle.kts",
             "requirements.txt", "pyproject.toml", ".env.example"}
SKIP_PARTS = ("node_modules/", "/node_modules", "vendor/", "archive", "archives/", "dist/", "build/")
MAX_MANIFESTS = 10

# libellé -> (types de fichiers concernés, motif cherché dans le contenu, en minuscules)
TECHS = {
    "React": ("package.json", r'"react"\s*:'),
    "Next.js": ("package.json", r'"next"\s*:'),
    "Vite": ("package.json", r'"vite"\s*:'),
    "Tailwind CSS": ("package.json", r'"tailwindcss"\s*:'),
    "Node.js (Express)": ("package.json", r'"express"\s*:'),
    "React Native": ("package.json", r'"react-native"\s*:'),
    "Flutter": ("pubspec.yaml", r"^\s*flutter\s*:"),
    "Riverpod": ("pubspec.yaml", r"riverpod"),
    "Spring Boot": ("pom.xml build.gradle build.gradle.kts", r"spring-boot"),
    "FastAPI": ("requirements.txt pyproject.toml", r"fastapi"),
    "Django": ("requirements.txt pyproject.toml", r"^\s*django"),
    "PyTorch": ("requirements.txt pyproject.toml", r"^\s*torch"),
    "scikit-learn": ("requirements.txt pyproject.toml", r"scikit-learn|sklearn"),
    "Streamlit": ("requirements.txt pyproject.toml", r"streamlit"),
    "Hugging Face": ("requirements.txt pyproject.toml", r"transformers"),
    "Supabase": ("package.json pubspec.yaml requirements.txt pyproject.toml", r"supabase"),
    "API Anthropic": ("package.json requirements.txt pyproject.toml .env.example", r"anthropic"),
    "OpenRouter": (".env.example package.json requirements.txt", r"openrouter"),
}


def detect_techs(paths, texts):
    """paths : chemins du dépôt ; texts : {chemin: contenu} des manifestes lus."""
    found = set()
    lower = [p.lower() for p in paths]
    if any(p.endswith("dockerfile") or "docker-compose" in p for p in lower):
        found.add("Docker")
    if any(p.startswith(".github/workflows/") for p in lower):
        found.add("GitHub Actions")
    if any(p.startswith("n8n/") or "/n8n/" in p for p in lower):
        found.add("n8n")
    for path, content in texts.items():
        base = path.rsplit("/", 1)[-1].lower()
        body = content.lower()
        for label, (kinds, pattern) in TECHS.items():
            if base in kinds.split() and re.search(pattern, body, re.M):
                found.add(label)
    return sorted(found)


# --------------------------------------------------------------------------- collecte
def api_get(path, token):
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "profile-stats-bot"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp), resp.headers.get("Link", "")


def paginate(path, token):
    page, out = 1, []
    sep = "&" if "?" in path else "?"
    while True:
        data, link = api_get(f"{path}{sep}per_page=100&page={page}", token)
        out.extend(data)
        if 'rel="next"' not in link:
            return out
        page += 1


def fetch_techs(full_name, token):
    try:
        tree, _ = api_get(f"/repos/{full_name}/git/trees/HEAD?recursive=1", token)
        paths = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob"]
    except urllib.error.HTTPError:
        return []
    wanted = [p for p in paths
              if p.rsplit("/", 1)[-1] in MANIFESTS and not any(s in p.lower() for s in SKIP_PARTS)][:MAX_MANIFESTS]
    texts = {}
    for p in wanted:
        try:
            data, _ = api_get(f"/repos/{full_name}/contents/{urllib.parse.quote(p)}", token)
            texts[p] = base64.b64decode(data.get("content", "")).decode("utf-8", "ignore")
        except (urllib.error.HTTPError, ValueError):
            continue
    return detect_techs(paths, texts)


def collect(token):
    me, _ = api_get("/user", token)
    owners = {o.strip().lower() for o in os.environ.get("STATS_OWNERS", "").split(",") if o.strip()}
    owners = owners or {me["login"].lower()}
    excluded = {x.strip().lower() for x in os.environ.get("STATS_EXCLUDE", "").split(",") if x.strip()}
    repos = paginate("/user/repos?visibility=all&affiliation=owner,organization_member", token)
    kept = []
    for r in repos:
        full = r["full_name"].lower()
        if r["fork"] or r["owner"]["login"].lower() not in owners or full in excluded:
            continue
        try:
            langs, _ = api_get(f"/repos/{r['full_name']}/languages", token)
        except urllib.error.HTTPError:
            langs = {}
        kept.append({"created": r["created_at"], "private": r["private"], "langs": langs,
                     "techs": fetch_techs(r["full_name"], token)})
    return kept


# --------------------------------------------------------------------------- calcul
def aggregate(repos):
    langs, nrepos, years, techs = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for r in repos:
        years[int(r["created"][:4])] += 1
        for k, v in r["langs"].items():
            if k not in EXCLUDED and v > 0:
                langs[k] += v
                nrepos[k] += 1
        for t in r.get("techs", []):
            techs[t] += 1
    return langs, nrepos, years, techs


def plural(n, word="projet"):
    return f"{n} {word}{'s' if n > 1 else ''}"


# --------------------------------------------------------------------------- rendu
def frame(t, w, h, title, subtitle, defs):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">',
            f'<defs>{defs}</defs>',
            f'<rect width="{w}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["grid"]}"/>',
            f'<text x="24" y="34" {FONT} font-size="18" font-weight="600" fill="{t["fg"]}">{title}</text>',
            f'<text x="24" y="54" {FONT} font-size="12" fill="{t["sub"]}">{subtitle}</text>']


def hgradient(t):
    return f'<linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{t["c1"]}"/><stop offset="1" stop-color="{t["c2"]}"/></linearGradient>'


def lang_chart(t, rows, total, n):
    row_h, top, W, L, R = 36, 70, 760, 150, 190
    h = 60 + row_h * len(rows) + 20
    peak = max(v for _, v, _ in rows) or 1
    s = frame(t, W, h, "Langages", f"Volume de code sur {n} dépôts (privés et publics, hors notebooks et balisage)", hgradient(t))
    for i, (name, v, count) in enumerate(rows):
        y = top + i * row_h
        w = (W - L - R) * v / peak
        fill = t["grid"] if name == "Autres" else "url(#g)"
        extra = f" · {plural(count)}" if count else ""
        s.append(f'<text x="24" y="{y + 16}" {FONT} font-size="13" fill="{t["fg"]}">{name}</text>')
        s.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="22" rx="5" fill="{fill}"/>')
        s.append(f'<text x="{L + w + 8:.1f}" y="{y + 16}" {FONT} font-size="12" fill="{t["sub"]}">{100 * v / total:.1f} %{extra}</text>')
    s.append("</svg>")
    return "\n".join(s)


def tech_chart(t, rows, n):
    row_h, top, W, L, R = 32, 70, 760, 150, 110
    h = 60 + row_h * len(rows) + 20
    peak = max(v for _, v in rows) or 1
    s = frame(t, W, h, "Technologies", f"Nombre de projets utilisant chaque technologie, sur {n} dépôts", hgradient(t))
    for i, (name, v) in enumerate(rows):
        y = top + i * row_h
        w = (W - L - R) * v / peak
        s.append(f'<text x="24" y="{y + 15}" {FONT} font-size="13" fill="{t["fg"]}">{name}</text>')
        s.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="20" rx="5" fill="url(#g)"/>')
        s.append(f'<text x="{L + w + 8:.1f}" y="{y + 15}" {FONT} font-size="12" fill="{t["sub"]}">{plural(v)}</text>')
    s.append("</svg>")
    return "\n".join(s)


def year_chart(t, series):
    W, H, L, B = 760, 300, 56, 56
    peak = max([v for _, v in series] + [1])
    ymax = ((peak + 4) // 5) * 5
    top, ph, pw = 74, H - 90 - B + 20, W - L - 24
    step = 5 if ymax > 10 else 2
    grad = f'<linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{t["c2"]}"/><stop offset="1" stop-color="{t["c1"]}"/></linearGradient>'
    s = frame(t, W, H, "Rythme de création", "Nouveaux dépôts par année (l'année en cours n'est pas terminée)", grad)
    for g in range(0, ymax + 1, step):
        y = top + ph - ph * g / ymax
        s.append(f'<line x1="{L}" x2="{W - 24}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["grid"]}" stroke-width="1"/>')
        s.append(f'<text x="{L - 8}" y="{y + 4:.1f}" text-anchor="end" {FONT} font-size="11" fill="{t["sub"]}">{g}</text>')
    bw = pw / len(series)
    for i, (label, v) in enumerate(series):
        h = ph * v / ymax
        x = L + i * bw + bw * 0.2
        y = top + ph - h
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw * 0.6:.1f}" height="{h:.1f}" rx="5" fill="url(#g)"/>')
        s.append(f'<text x="{x + bw * 0.3:.1f}" y="{y - 6:.1f}" text-anchor="middle" {FONT} font-size="12" fill="{t["fg"]}">{v}</text>')
        s.append(f'<text x="{x + bw * 0.3:.1f}" y="{top + ph + 20:.1f}" text-anchor="middle" {FONT} font-size="11" fill="{t["sub"]}">{label}</text>')
    s.append("</svg>")
    return "\n".join(s)


def write_if_changed(path, content):
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def update_readme(n, private, today):
    text = README.read_text(encoding="utf-8")
    block = (f"<!-- stats:start -->\nStatistiques calculées sur l'ensemble de mes dépôts, privés comme publics "
             f"({n} dépôts analysés, dont {private} privés). Mise à jour automatique chaque semaine, "
             f"dernière exécution le {today.day} {MONTHS[today.month - 1]} {today.year}.\n<!-- stats:end -->")
    new, count = re.subn(r"<!-- stats:start -->.*?<!-- stats:end -->", block, text, flags=re.S)
    if count == 0:
        print("Marqueurs <!-- stats:start --> introuvables dans le README : texte non mis à jour.")
        return False
    return write_if_changed(README, new)


def main():
    fixture = os.environ.get("STATS_FIXTURE")
    if fixture:
        repos = json.loads(pathlib.Path(fixture).read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GH_TOKEN", "").strip()
        if not token:
            print("Secret PROFILE_STATS_TOKEN absent : graphiques conservés tels quels.")
            return 0
        try:
            repos = collect(token)
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            print(f"Échec de la collecte ({type(exc).__name__}) : graphiques conservés tels quels.")
            return 1
    if not repos:
        print("Aucun dépôt retenu : graphiques conservés tels quels (vérifier STATS_OWNERS).")
        return 1

    today = datetime.date.today()
    langs, nrepos, years, techs = aggregate(repos)
    total = sum(langs.values())
    if total == 0:
        print("Aucun volume de code détecté : graphiques conservés tels quels.")
        return 1

    top = langs.most_common(7)
    rows = [(LABELS.get(k, k), v, nrepos[k]) for k, v in top] + [("Autres", total - sum(v for _, v in top), 0)]
    tech_rows = techs.most_common(TECHS_SHOWN)
    first = min(years)
    series = [(str(y), years.get(y, 0)) for y in range(first, today.year + 1)]

    changed = False
    for name, theme in THEMES.items():
        changed |= write_if_changed(ASSETS / f"langages-{name}.svg", lang_chart(theme, rows, total, len(repos)))
        if tech_rows:
            changed |= write_if_changed(ASSETS / f"technologies-{name}.svg", tech_chart(theme, tech_rows, len(repos)))
        changed |= write_if_changed(ASSETS / f"rythme-{name}.svg", year_chart(theme, series))
    changed |= update_readme(len(repos), sum(1 for r in repos if r["private"]), today)
    print(f"{len(repos)} dépôts analysés ; fichiers {'mis à jour' if changed else 'inchangés'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

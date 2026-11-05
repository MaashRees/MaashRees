#!/usr/bin/env python3
"""Met à jour les graphiques du profil (langages et rythme de création des dépôts).

Le script lit les dépôts via l'API GitHub, calcule des chiffres agrégés puis réécrit
les SVG de `assets/` et le paragraphe balisé du README. Aucun nom de dépôt n'est écrit
dans les fichiers produits ni affiché dans les journaux : seuls des totaux le sont.

Variables d'environnement (à définir comme secrets du dépôt) :
  GH_TOKEN      jeton d'accès en lecture aux dépôts, privés compris (obligatoire)
  STATS_OWNERS  comptes et organisations à inclure, séparés par des virgules
                (facultatif, par défaut : le compte propriétaire du jeton uniquement)
  STATS_EXCLUDE dépôts à ignorer, « propriétaire/nom » séparés par des virgules (facultatif)

Pour tester sans réseau : STATS_FIXTURE=chemin/vers/fichier.json (liste d'objets
{"created": "...", "private": bool, "langs": {"Python": 123}}).
"""
import collections
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
API = "https://api.github.com"

# langages comptés comme du « code » (on exclut données, balisage et scripts annexes)
EXCLUDED = {"Jupyter Notebook", "HTML", "CSS", "Makefile", "Dockerfile", "Shell", "PowerShell", "Batchfile"}
LABELS = {"PLpgSQL": "SQL (PL/pgSQL)"}
QUARTERS_SHOWN = 8
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]

THEMES = {
    "light": dict(bg="#ffffff", fg="#1f2328", sub="#59636e", grid="#d1d9e0", c1="#0891b2", c2="#9333ea"),
    "dark": dict(bg="#030303", fg="#ffffff", sub="#a1a1a1", grid="#262626", c1="#00b8db", c2="#ad46ff"),
}
FONT = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'


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
        kept.append({"created": r["created_at"], "private": r["private"], "langs": langs})
    return kept


# --------------------------------------------------------------------------- calcul
def aggregate(repos):
    langs, quarters = collections.Counter(), collections.Counter()
    for r in repos:
        y, m = int(r["created"][:4]), int(r["created"][5:7])
        quarters[(y, (m - 1) // 3 + 1)] += 1
        for k, v in r["langs"].items():
            if k not in EXCLUDED:
                langs[k] += v
    return langs, quarters


def last_quarters(n, today):
    y, q = today.year, (today.month - 1) // 3 + 1
    out = []
    for _ in range(n):
        out.append((y, q))
        q -= 1
        if q == 0:
            y, q = y - 1, 4
    return list(reversed(out))


# --------------------------------------------------------------------------- rendu
def lang_chart(t, rows, total, n):
    row_h, top = 36, 70
    height = 60 + row_h * len(rows) + 20
    W, L, R = 760, 150, 90
    peak = max(v for _, v in rows) or 1
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Répartition du code par langage">',
         f'<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{t["c1"]}"/><stop offset="1" stop-color="{t["c2"]}"/></linearGradient></defs>',
         f'<rect width="{W}" height="{height}" rx="12" fill="{t["bg"]}" stroke="{t["grid"]}"/>',
         f'<text x="24" y="34" {FONT} font-size="18" font-weight="600" fill="{t["fg"]}">Langages</text>',
         f'<text x="24" y="54" {FONT} font-size="12" fill="{t["sub"]}">Volume de code sur {n} dépôts (privés et publics, hors notebooks et balisage)</text>']
    for i, (name, v) in enumerate(rows):
        y = top + i * row_h
        w = (W - L - R) * v / peak
        fill = t["grid"] if name == "Autres" else "url(#g)"
        s.append(f'<text x="24" y="{y + 16}" {FONT} font-size="13" fill="{t["fg"]}">{name}</text>')
        s.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="22" rx="5" fill="{fill}"/>')
        s.append(f'<text x="{L + w + 8:.1f}" y="{y + 16}" {FONT} font-size="12" fill="{t["sub"]}">{100 * v / total:.1f} %</text>')
    s.append("</svg>")
    return "\n".join(s)


def quarter_chart(t, series):
    W, H, L, B = 760, 300, 56, 56
    peak = max([v for _, v in series] + [1])
    ymax = ((peak + 4) // 5) * 5
    top = 74
    ph = H - 90 - B + 20
    pw = W - L - 24
    step = 5 if ymax > 10 else 2
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Dépôts créés par trimestre">',
         f'<defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{t["c2"]}"/><stop offset="1" stop-color="{t["c1"]}"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="12" fill="{t["bg"]}" stroke="{t["grid"]}"/>',
         f'<text x="24" y="34" {FONT} font-size="18" font-weight="600" fill="{t["fg"]}">Rythme de création</text>',
         f'<text x="24" y="54" {FONT} font-size="12" fill="{t["sub"]}">Nouveaux dépôts par trimestre (le dernier trimestre est en cours)</text>']
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
    langs, quarters = aggregate(repos)
    total = sum(langs.values())
    if total == 0:
        print("Aucun volume de code détecté : graphiques conservés tels quels.")
        return 1
    top = langs.most_common(7)
    rows = [(LABELS.get(k, k), v) for k, v in top] + [("Autres", total - sum(v for _, v in top))]
    series = [(f"{y} T{q}", quarters.get((y, q), 0)) for y, q in last_quarters(QUARTERS_SHOWN, today)]

    changed = False
    for name, theme in THEMES.items():
        changed |= write_if_changed(ASSETS / f"langages-{name}.svg", lang_chart(theme, rows, total, len(repos)))
        changed |= write_if_changed(ASSETS / f"rythme-{name}.svg", quarter_chart(theme, series))
    changed |= update_readme(len(repos), sum(1 for r in repos if r["private"]), today)
    print(f"{len(repos)} dépôts analysés ; fichiers {'mis à jour' if changed else 'inchangés'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
fetch_jira.py — Descarga todas las incidencias de Jira y genera data.json
Ejecutado por GitHub Actions cada 24h. Requiere la variable de entorno JIRA_TOKEN.
"""
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError

JIRA_BASE   = "https://proyectos.gco.global"
JIRA_PATH   = "/rest/api/2/search"
JIRA_JQL    = "project=INCASUR AND status != Closed"
JIRA_FIELD  = "customfield_15400"
JIRA_BROWSE = f"{JIRA_BASE}/browse/"

TOKEN = os.environ.get("JIRA_TOKEN", "")
if not TOKEN:
    print("ERROR: Variable de entorno JIRA_TOKEN no definida.")
    sys.exit(1)

def fetch_page(start_at):
    params = urlencode({
        "jql":        JIRA_JQL,
        "expand":     "changelog",
        "startAt":    start_at,
        "maxResults": 50,
    })
    url = f"{JIRA_BASE}{JIRA_PATH}?{params}"
    req = Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept":        "application/json",
    })
    try:
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except URLError as e:
        print(f"Error al conectar con Jira: {e}")
        sys.exit(1)

def fetch_all():
    all_issues, start_at, total = [], 0, 1
    while start_at < total:
        data   = fetch_page(start_at)
        total  = data.get("total", 0)
        if not total:
            break
        all_issues.extend(data.get("issues", []))
        start_at += 50
        print(f"  Descargadas {min(start_at, total)}/{total} incidencias...")
    return all_issues

def process(issues):
    now    = datetime.now(timezone.utc)
    CLOSED = {"CLOSED","CERRADO","RESOLVED","RESUELTO","DONE"}
    rows   = []

    for issue in issues:
        key    = issue["key"]
        fields = issue["fields"]
        estado = fields.get("status", {}).get("name", "Desconocido")
        if estado.upper() in CLOSED:
            continue

        from datetime import datetime as dt
        def parse(s):
            # Compatible con Python 3.6 (GitHub runners)
            s = s.rstrip("Z")
            if "+" in s:
                s = s[:s.index("+")]
            try:
                return dt.fromisoformat(s).replace(tzinfo=timezone.utc)
            except:
                import re
                s = re.sub(r'\.\d+$', '', s)
                return dt.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

        fc  = parse(fields["created"])
        um  = parse(fields["updated"])
        dias_a = max(0, (now - fc).days)
        dias_m = (now - um).days

        hist = sorted(
            issue.get("changelog", {}).get("histories", []),
            key=lambda h: h["created"]
        )

        d_act   = "Desconocido"
        f_ent   = fc
        dptos   = []
        v_fo    = 0

        for h in hist:
            fh = parse(h["created"])
            for it in h["items"]:
                campo = (it.get("field") or "").lower()
                val   = (it.get("toString") or "").strip()
                if not val or val.upper() == "NONE":
                    continue
                if campo in ("component", "component/s"):
                    if val not in dptos:
                        dptos.append(val)
                    if val.upper() == "FRONT OFFICE":
                        v_fo += 1
                    elif d_act != val:
                        d_act = val
                        f_ent = fh

        if d_act == "Desconocido" and fields.get("components"):
            b = fields["components"][0]["name"]
            if b and b.upper() != "NONE":
                d_act = b
                if b not in dptos:
                    dptos.append(b)
                if b.upper() == "FRONT OFFICE":
                    v_fo = 1

        dias_d = max(0, (now - f_ent).days)

        try:
            n_rec = int(float(fields.get(JIRA_FIELD) or 0))
        except:
            n_rec = 0

        rows.append({
            "Incidencia":                      key,
            "Fecha de Creación":               fc.strftime("%d/%m/%Y"),
            "Estado":                          estado,
            "Departamento Responsable":        d_act,
            "Días Abierta Totales":            dias_a,
            "Días atascada en Dpto Actual":    dias_d,
            "Días desde Última Modificación":  dias_m,
            "Rebotes a Front-Office":          v_fo,
            "Nº Reclamaciones":                n_rec,
            "Ruta de Departamentos":           " → ".join(dptos) if dptos else d_act,
            "Resumen":                         fields.get("summary", ""),
            "URL":                             f"{JIRA_BROWSE}{key}",
        })

    rows.sort(key=lambda r: r["Días Abierta Totales"], reverse=True)
    return rows

if __name__ == "__main__":
    print("Conectando con Jira...")
    issues = fetch_all()
    print(f"Procesando {len(issues)} incidencias...")
    rows = process(issues)
    print(f"Incidencias activas: {len(rows)}")

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total":      len(rows),
        "issues":     rows,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ data.json generado correctamente.")

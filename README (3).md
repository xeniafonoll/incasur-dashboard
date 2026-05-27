# 📊 INCASUR Dashboard

Dashboard accesible desde cualquier navegador con link de GitHub Pages.  
Los datos se actualizan automáticamente cada día desde tu ordenador.

## Cómo funciona

```
Tu PC (cada día 8:00h)  →  fetch_jira.py  →  data.json  →  git push  →  GitHub Pages
Cualquier navegador     →  lee data.json  →  dashboard instantáneo
```

---

## Puesta en marcha

### Paso 1 — Instalar Git en tu ordenador (si no lo tienes)
Descárgalo de https://git-scm.com/download/win e instálalo con las opciones por defecto.

### Paso 2 — Clonar el repositorio en tu ordenador
Abre CMD o PowerShell y ejecuta:
```
git clone https://github.com/TU_USUARIO/incasur-dashboard.git C:\incasur-dashboard
```

### Paso 3 — Editar actualizar.bat
Abre `actualizar.bat` con el Bloc de notas y cambia estas dos líneas:
```
set JIRA_TOKEN=PON_AQUI_TU_TOKEN
set REPO_DIR=C:\incasur-dashboard
```

### Paso 4 — Probar que funciona
Haz doble clic en `actualizar.bat`. Debe:
1. Descargar los datos de Jira (puede tardar 1-2 minutos)
2. Actualizar `data.json`
3. Hacer `git push` al repositorio

Si es la primera vez que usas git en ese ordenador, te pedirá usuario y contraseña de GitHub.

### Paso 5 — Activar GitHub Pages
En GitHub → tu repositorio → Settings → Pages → Source: main / root → Save

### Paso 6 — Crear la tarea programada (para que corra solo cada día)
Haz clic derecho sobre `crear_tarea_programada.ps1` → **Ejecutar con PowerShell**.
Acepta si pide permisos de administrador.

Esto crea una tarea en el Programador de Windows que ejecuta `actualizar.bat` cada día a las 8:00h.
**El ordenador tiene que estar encendido a esa hora.**

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `index.html` | El dashboard web (GitHub Pages) |
| `data.json` | Datos procesados de Jira (se regenera cada día) |
| `fetch_jira.py` | Descarga y procesa los datos de Jira |
| `actualizar.bat` | Script que ejecuta fetch_jira.py y hace git push |
| `crear_tarea_programada.ps1` | Registra la tarea automática en Windows |

---

## Si el ordenador no estaba encendido a las 8:00h

La tarea tiene activado **"Iniciar si se perdió la ejecución"** (`-StartWhenAvailable`),  
así que se ejecutará automáticamente en cuanto enciendas el ordenador ese día.

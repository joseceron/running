# Guía de conexión a fuentes científicas y análisis con SDK Anthropic PDF

Este documento describe cómo conectarse a Scopus, Web of Science y el SDK de Anthropic para PDFs,
y establece el flujo de trabajo obligatorio para cualquier consulta de investigación: **toda
afirmación debe estar respaldada por artículos científicos descargados y analizados con el SDK**.

## Limitación crítica: Scopus y WOS no entregan PDFs por API

Las APIs de Scopus y Web of Science **solo proveen metadatos y abstracts**. El PDF completo
requiere acceso institucional (IP de la universidad) o un token de licencia separado que solo
tienen instituciones con contrato activo — la `SCOPUS_API_KEY` y la `WOS_API_KEY` no dan acceso
al full-text.

Por tanto, el flujo real de obtención de PDFs es:

| Ruta                        | Cómo funciona                                                  | Cuándo usarla          |
|-----------------------------|----------------------------------------------------------------|------------------------|
| **Red institucional**       | Descargar el PDF manualmente desde el navegador en la red de la universidad | Artículos de pago bajo licencia UNICAUCA/institución |
| **Unpaywall** (API abierta) | Busca versión abierta por DOI; devuelve URL directa al PDF     | Primera opción automática para artículos con versión OA |
| **PubMed Central**          | PDFs de ciencias biomédicas con financiamiento público         | Artículos NIH, Wellcome, etc. |
| **SciELO**                  | Revistas latinoamericanas e iberoamericanas de acceso abierto  | Revistas colombianas, brasileñas, etc. |
| **arXiv / bioRxiv**         | Preprints de física, computación, biología                     | Cuando el artículo tiene preprint público |
| **Repositorio institucional** | Muchas universidades publican versiones aceptadas (postprint) | Búsqueda manual por autor + universidad |

**Flujo automatizable con Unpaywall** (sin coste, sin cuenta):
```bash
# Verificar si hay versión abierta de un DOI
curl "https://api.unpaywall.org/v2/10.1016/j.foodchem.2023.XXXXX?email=joseluisceron13@gmail.com" \
  | jq '.best_oa_location.url_for_pdf'

# Si devuelve una URL (no null), descargar:
curl -L "https://..." -o pdfs/autor_2023.pdf
```

**Lo que Scopus y WOS sí aportan por API** (y lo que usamos):
- Lista de DOIs relevantes para una consulta temática
- Metadatos: título, autores, revista, año, cuartil, número de citas
- Abstract para filtrar qué artículos vale la pena descargar y analizar
- Datos para construir el diagrama de flujo PRISMA

**Implicación práctica**: en cada sesión de análisis, los PDFs a analizar con el SDK deben estar
ya descargados en la carpeta `pdfs/`. Esta guía describe cómo obtenerlos y cómo hacer que el SDK
los analice una vez disponibles.

---

## Variables de entorno requeridas

Todas las claves se almacenan en el archivo `.env` en la raíz del proyecto. Nunca escribir los
valores directamente en el código.

| Variable            | Uso                                        |
|---------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY` | Autenticación en la API de Anthropic       |
| `SCOPUS_API_KEY`    | Autenticación en la API de Scopus (Elsevier) |
| `WOS_API_KEY`       | Autenticación en la API de Web of Science  |

Carga en Node.js:
```js
import dotenv from "dotenv";
dotenv.config({ path: "../.env" }); // ajusta la ruta según la ubicación del script

const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const SCOPUS_KEY    = process.env.SCOPUS_API_KEY;
const WOS_KEY       = process.env.WOS_API_KEY;
```

Carga en Python:
```python
from dotenv import load_dotenv
import os

load_dotenv("../.env")  # ajusta la ruta según la ubicación del script

ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SCOPUS_KEY    = os.environ["SCOPUS_API_KEY"]
WOS_KEY       = os.environ["WOS_API_KEY"]
```

---

## 1. Conexión a Scopus

### 1.1 Búsqueda de artículos

Endpoint: `https://api.elsevier.com/content/search/scopus`

```python
import requests

headers = {
    "X-ELS-APIKey": SCOPUS_KEY,
    "Accept": "application/json"
}

params = {
    "query": "TITLE-ABS-KEY(cassava AND starch AND edible)",
    "count": 25,
    "start": 0,
    "field": "dc:title,prism:doi,dc:creator,prism:publicationName,prism:coverDate,citedby-count"
}

resp = requests.get(
    "https://api.elsevier.com/content/search/scopus",
    headers=headers,
    params=params
)
results = resp.json()["search-results"]["entry"]
```

Campos clave en cada resultado:
- `prism:doi` — DOI para descargar el PDF o recuperar metadatos
- `dc:title` — título del artículo
- `prism:publicationName` — nombre de la revista
- `citedby-count` — número de citas (indicador de impacto)

### 1.2 Recuperar abstract completo

```python
doi = "10.1016/j.foodchem.2023.xxxxxx"
resp = requests.get(
    f"https://api.elsevier.com/content/abstract/doi/{doi}",
    headers={**headers, "Accept": "application/json"}
)
abstract = resp.json()["abstracts-retrieval-response"]["coredata"]["dc:description"]
```

### 1.3 Límites de la API

- 25 resultados por página; paginar con `start=0, 25, 50, ...`
- Máximo 5 000 resultados por consulta con clave estándar
- Respetar 1 s entre peticiones para no saturar el rate limit
- El acceso al PDF completo requiere IP institucional o token de licencia separado

---

## 2. Conexión a Web of Science

### 2.1 Búsqueda con la API REST (Starter/Expanded)

Endpoint base: `https://api.clarivate.com/apis/wos-starter/v1`

```python
headers = {
    "X-ApiKey": WOS_KEY,
    "Accept": "application/json"
}

params = {
    "q": "TS=(yam starch AND thermoplastic)",   # TS = Topic (título + abstract + palabras clave)
    "db": "WOS",                                 # Web of Science Core Collection
    "limit": 10,
    "page": 1
}

resp = requests.get(
    "https://api.clarivate.com/apis/wos-starter/v1/documents",
    headers=headers,
    params=params
)
records = resp.json()["hits"]
```

Campos útiles por registro:
- `uid` — identificador único WOS (ej. `WOS:000123456789012`)
- `title.value` — título
- `source.publishYear` — año
- `source.sourceTitle` — revista
- `keywords.authorKeywords` — palabras clave del autor

### 2.2 Operadores de búsqueda WOS

| Operador | Función                                      |
|----------|----------------------------------------------|
| `TS=`    | Topic: título + abstract + palabras clave    |
| `TI=`    | Solo título                                  |
| `AU=`    | Autor                                        |
| `SO=`    | Nombre de la revista                         |
| `PY=`    | Año de publicación (ej. `PY=2020-2024`)      |
| `AND`, `OR`, `NOT` | Operadores booleanos estándar     |

### 2.3 Límites de la API

- 1 000 registros por consulta (con clave Starter)
- 50 ms de pausa recomendada entre peticiones
- Sin acceso a PDF completo vía API; el enlace al full-text requiere licencia institucional

---

## 3. SDK Anthropic para análisis de PDFs

### 3.1 Instalación

```bash
npm install @anthropic-ai/sdk dotenv   # Node.js
# o
pip install anthropic python-dotenv    # Python
```

### 3.2 Enviar un PDF como documento (≤ 100 páginas combinadas)

```js
import Anthropic from "@anthropic-ai/sdk";
import fs from "node:fs";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const pdfBase64 = fs.readFileSync("articulo.pdf").toString("base64");

const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 4096,
  messages: [{
    role: "user",
    content: [
      {
        type: "document",
        source: { type: "base64", media_type: "application/pdf", data: pdfBase64 }
      },
      { type: "text", text: "Extrae los hallazgos principales, metodología y conclusiones." }
    ]
  }]
});

console.log(response.content[0].text);
```

### 3.3 PDFs grandes (> 50 páginas): extraer texto primero

Cuando el PDF supera 50 páginas o el total combinado supera 100 páginas, enviar como texto plano
con `cache_control` para evitar el error `A maximum of 100 PDF pages may be provided`.

```bash
# Extraer texto preservando layout (tablas, columnas)
pdftotext -layout articulo.pdf articulo.txt
```

```js
const pdfText = fs.readFileSync("articulo.txt", "utf8");

const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 8192,
  messages: [{
    role: "user",
    content: [
      {
        type: "text",
        text: "=== CONTENIDO DEL ARTÍCULO ===\n\n" + pdfText,
        cache_control: { type: "ephemeral" }   // evita reprocesar en llamadas múltiples
      },
      { type: "text", text: "Analiza la metodología estadística y los resultados numéricos." }
    ]
  }]
});
```

### 3.4 Respuestas largas: streaming obligatorio

Para `max_tokens > 8 000` usar streaming para evitar timeout:

```js
async function streamFinalText(args, label) {
  const stream = await client.messages.stream(args);
  let lastTick = Date.now();
  for await (const _e of stream) {
    if (Date.now() - lastTick > 30_000) {
      process.stdout.write(`  · ${label} en curso…\n`);
      lastTick = Date.now();
    }
  }
  return (await stream.finalMessage()).content[0].text;
}
```

### 3.5 Retry ante errores transitorios

```js
const TRANSIENT = new Set([408, 425, 429, 500, 502, 503, 504, 529]);

async function withRetry(fn, label, maxAttempts = 8) {
  let attempt = 0, lastErr;
  while (attempt < maxAttempts) {
    try { return await fn(); } catch (err) {
      if (!TRANSIENT.has(err?.status) || attempt === maxAttempts - 1) throw err;
      const ra = err?.headers?.["retry-after"];
      const wait = Math.max(ra ? Number(ra) * 1000 : 0, 5000 * Math.pow(2, attempt));
      console.warn(`  ⚠ ${label}: ${err.status}, intento ${attempt + 1}; espero ${Math.round(wait/1000)}s…`);
      await new Promise(r => setTimeout(r, wait));
      attempt++; lastErr = err;
    }
  }
  throw lastErr;
}
```

### 3.6 Límites operativos

| Restricción                          | Valor                                     |
|--------------------------------------|-------------------------------------------|
| Páginas combinadas por mensaje       | 100 páginas máximo                        |
| Rate limit Opus (tier por defecto)   | ~30 000 tokens de entrada / minuto        |
| Rate limit Sonnet (tier por defecto) | ~80 000 tokens de entrada / minuto        |
| `max_tokens` sin streaming           | Seguro hasta ~8 000; streaming por encima |
| Modelo recomendado para PDFs grandes | `claude-sonnet-4-6`                       |

---

## 4. Flujo de trabajo obligatorio para cualquier consulta

**Toda respuesta sobre un tema científico debe estar respaldada por artículos descargados y
analizados con el SDK.** El flujo es:

```
1. Definir la consulta
       │
       ▼
2. Buscar en Scopus y/o WOS  [API → metadatos + abstracts solamente]
   → Recuperar lista de DOIs relevantes con título, autores, revista y año
   → Filtrar por abstract: descartar los que no son pertinentes
   → Anotar cuáles tienen versión en acceso abierto (campo OA en Scopus)
       │
       ▼
3. Obtener PDFs  [esta etapa NO es automática vía Scopus/WOS]
   → OPCIÓN A (automática): consultar Unpaywall por DOI → descargar si hay URL abierta
   → OPCIÓN B (manual): descargar desde la red institucional de la universidad
   → OPCIÓN C (automática): buscar en PubMed Central, SciELO, arXiv según la disciplina
   → Guardar en pdfs/autor_año.pdf
       │
       ▼
4. Extraer texto si el PDF > 50 pp
   → pdftotext -layout pdfs/autor_año.pdf txt/autor_año.txt
       │
       ▼
5. Analizar con SDK Anthropic  [aquí entra el poder del SDK]
   → Una llamada por artículo (o lote si todos ≤ 100 pp combinadas)
   → El modelo lee tablas, figuras, ecuaciones y texto corrido del PDF original
   → Prompt adaptado al objetivo: metodología, resultados numéricos, tablas, figuras
   → cache_control: ephemeral para hacer múltiples preguntas sobre el mismo PDF sin re-tokenizar
       │
       ▼
6. Sintetizar hallazgos
   → Consolidar en un Markdown con citas (Autor, año, página o tabla)
   → Nunca afirmar datos que no estén en el PDF analizado
   → Marcar con [REQUIERE PDF] lo que solo se encontró en el abstract
```

### 4.1 Ejemplo: analizar una tabla de resultados en un artículo

```js
const prompt = `
El artículo contiene tablas con datos experimentales.
1. Extrae TODAS las tablas y reconstruye su contenido en formato Markdown.
2. Para cada tabla indica: título, unidades, n° de tratamientos y la variable respuesta principal.
3. Identifica si los valores muestran diferencias estadísticamente significativas (p < 0.05).
4. No inventes valores; transcribe exactamente lo que aparece en el PDF.
`;
```

### 4.2 Ejemplo: extraer metodología de diseño experimental

```js
const prompt = `
Del sección Materiales y Métodos extrae:
- Diseño experimental (tipo, factores, niveles, réplicas)
- Variables independientes y dependientes con sus unidades
- Métodos analíticos empleados (normas AOAC, ISO, ASTM citadas)
- Software estadístico y pruebas post-hoc aplicadas
Presenta la información en listas con viñetas. No añadas interpretaciones propias.
`;
```

---

## 5. Descarga de PDFs en acceso abierto

Cuando no hay acceso institucional, usar estas rutas:

```bash
# Unpaywall (busca versión abierta por DOI)
curl "https://api.unpaywall.org/v2/10.1016/j.foodchem.2023.XXXXX?email=tu@email.com" \
  | jq '.best_oa_location.url_for_pdf'

# PubMed Central (artículos biomédicos)
# Buscar PMC ID y descargar:
curl "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/pdf/" -o articulo.pdf

# SciELO (revistas latinoamericanas)
# URL directa al PDF disponible en la ficha del artículo
```

---

## 6. Estructura de carpetas recomendada para un análisis

```
proyecto/
├── .env                        ← claves (ANTHROPIC_API_KEY, SCOPUS_API_KEY, WOS_API_KEY)
├── pdfs/                       ← artículos descargados (no subir al repositorio)
│   ├── autor1_2024.pdf
│   └── autor2_2023.pdf
├── txt/                        ← textos extraídos con pdftotext (PDFs > 50 pp)
│   ├── autor1_2024.txt
│   └── autor2_2023.txt
├── scripts/
│   ├── buscar_scopus.mjs       ← consulta y guarda DOIs/metadatos
│   ├── buscar_wos.mjs          ← consulta Web of Science
│   └── analizar_pdfs.mjs       ← carga PDFs/textos y llama al SDK
└── output/
    └── sintesis_hallazgos.md   ← resultado consolidado con citas
```

---

## 7. Reglas que aplican en todas las sesiones

1. **Nunca afirmar datos sin fuente**: cada cifra, porcentaje o conclusión debe citar el artículo
   del que proviene (Autor, año, página o tabla).
2. **Usar Sonnet para PDFs grandes**: `claude-sonnet-4-6` tiene rate limit superior al de Opus y
   es suficiente para extracción y síntesis de artículos científicos.
3. **`cache_control: ephemeral`** en el bloque del PDF cuando se van a hacer varias preguntas
   sobre el mismo documento; evita retokenizar en cada llamada.
4. **Streaming para outputs largos**: cualquier síntesis que supere ~10 páginas de salida debe
   usar `client.messages.stream(...)`.
5. **Documentar el origen**: en el Markdown de síntesis, incluir siempre la referencia completa
   (título, revista, DOI) de cada artículo analizado.

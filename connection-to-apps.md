# Metodología: Conectarse a apps de escritorio sin API pública

Caso de estudio: **Celeste** (ERP Java con RMI propietario).  
Aplicable a cualquier app de escritorio que gestione sesión de usuario y se comunique con un servidor.

---

## Resumen del enfoque

La idea central es **interceptar la comunicación real de la app** (no simularla a ciegas), construir un puente que replique exactamente esa sesión, y exponerla como un API HTTP propio.

```
App de escritorio ──► [protocolo propietario] ──► Servidor backend
        │
        │ (interceptamos aquí)
        ▼
  CelesteJavaBridge.java
  (reutiliza las mismas libs de la app, sin GUI)
        │
        ▼
  HTTP localhost:9191  ──►  Cloud Run  ──►  Firebase Functions  ──►  n8n
```

---

## Fase 1 — Entender el protocolo de la app

### 1.1 Interceptar tráfico con mitmproxy

```bash
# Instalar mitmproxy
pip install mitmproxy

# Lanzar Celeste a través del proxy
./launch-celeste-proxy.sh
# O manualmente:
mitmweb --listen-port 8888 --web-port 8081 -s capture_addon.py
# Configurar JVM para que use el proxy:
# java -Dhttp.proxyHost=localhost -Dhttp.proxyPort=8888 ...
```

El addon `capture_addon.py` guarda cada request/response en `/tmp/celeste_session.json`.

**Qué buscar en el tráfico:**
- URL del servidor backend y puerto
- Formato de autenticación (JWT, cookies, sesión propia)
- Tipo de serialización (JSON, XML, Java serialization binaria)
- Nombres de métodos llamados (son el "API" real de la app)

**En Celeste encontramos:**
- Protocolo: **Java RMI** (no HTTP) — los paquetes son serialización Java binaria
- URL RMI: `//134.209.69.212:1133/SME-Produccion-C3-Publica`
- Auth: login con RSA encrypt de password → servidor devuelve `sessionId`
- Bootstrap: la app primero hace HTTP a `wscv2.celestefacturacion.com:8443` para obtener la URL RMI

### 1.2 Identificar los JARs de la app

```bash
# Dónde están los JARs del cliente
ls /Library/Celeste/Cliente/
# CelesteLanzador.jar — lanzador
# recursos/produccion/CelesteMipyme.jar — lógica completa del cliente
```

Estos JARs contienen las **clases del protocolo** que se pueden reutilizar en un bridge.

---

## Fase 2 — Descubrir los métodos disponibles

### 2.1 Extraer y analizar el bytecode

```bash
mkdir -p /tmp/celeste_extract && cd /tmp/celeste_extract
jar -xf /Library/Celeste/Cliente/recursos/produccion/CelesteMipyme.jar

# Buscar todos los métodos expuestos por RMI (naming convention: Manejo*_NombreMetodo)
find . -name "*.class" | xargs strings 2>/dev/null | grep "^Manejo" | sort -u

# Buscar por dominio específico (productos, inventario, terceros...)
strings ./productos/manejo/ManejoProductos.class | grep -i "fisico\|stock\|cant\|export\|busqueda"
strings ./inventario/manejo/ManejoInventario.class | grep -i "stock\|bodega"
```

### 2.2 Inspeccionar firma de argumentos

```bash
# Ver los getters/setters de una clase de parámetros
javap -p /tmp/celeste_extract/parametros/productos/ParametrosTablaBusqueda_ProductosGeneral.class

# Ver strings y anotaciones
strings /tmp/celeste_extract/parametros/productos/ParametrosTablaBusqueda_ProductosGeneral.class | head -50
```

**Regla crítica — qué métodos funcionan vía bridge:**

| Tipo de args | ¿Funciona? | Razón |
|---|---|---|
| Solo primitivos: `Integer`, `String`, `Boolean` | ✅ Sí | Serialización estándar Java |
| Objetos de dominio del cliente (`ParametrosTablaBusqueda_*`) | ❌ No | Campos `transient` se pierden en RMI → el server recibe objetos incompletos |
| Enums del cliente | ✅ Sí (con truco) | Pasar como string `"ENUM:NOMBRE_ENUM"` — el bridge los resuelve por reflection |

### 2.3 Verificar un método nuevo

```bash
# Probar directamente contra el bridge local
curl -s http://localhost:9191/call \
  -H "Content-Type: application/json" \
  -d '{"method": "ManejoProductosBusquedas_getFisicoBodega", "args": [3745, 3]}'
# Respuesta esperada: "33" (BigDecimal serializado como JSON)

# Si el bridge no está corriendo localmente, usar el de Cloud Run (con auth)
TOKEN=$(gcloud auth print-identity-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://celeste-bridge-143096173578.us-east1.run.app/call" \
  -H "Content-Type: application/json" \
  -d '{"method": "ManejoProductosBusquedas_getFisicoBodega", "args": [3745, 3]}'
```

---

## Fase 3 — Construir el bridge Java

### 3.1 Estructura del bridge

El bridge (`CelesteJavaBridge.java`) es un proceso Java ligero que:
1. Se conecta al servidor RMI usando las mismas clases del JAR del cliente
2. Replica el login (RSA encrypt, `obtenerClavePublica` → `iniciarSesion`)
3. Expone un servidor HTTP en `localhost:9191` con endpoints simples
4. Node.js (`celeste-api.js`) lo llama vía axios y convierte la respuesta a JSON

```
celeste-api.js (Node.js)
    │  axios POST localhost:9191/call
    ▼
CelesteJavaBridge.java (HTTP server)
    │  carga CelesteMipyme.jar como classpath
    │  usa reflection para invocar métodos RMI
    ▼
RMI Server (134.209.69.212:1133)
    │
    ▼
Base de datos Celeste (PostgreSQL)
```

### 3.2 Login — replicar exactamente lo que hace la app

```java
// 1. Obtener clave pública RSA del servidor
Object pubKey = rmiServer.metodoGeneral("obtenerClavePublica", new Object[]{});

// 2. Encriptar password con RSA
Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
cipher.init(Cipher.ENCRYPT_MODE, (PublicKey) pubKey);
byte[] encrypted = cipher.doFinal(password.getBytes(StandardCharsets.UTF_8));
String encryptedB64 = Base64.getEncoder().encodeToString(encrypted);

// 3. Llamar iniciarSesion → devuelve sessionId y otrosDatos[]
Object result = rmiServer.iniciarSesion(username, encryptedB64, nit, empresaId);
// otrosDatos[5] = bodegaId (Integer) — guardarlo para stock queries
loginBodegaId = (Integer) otrosDatos[5];
```

### 3.3 Invocar métodos — el endpoint /call

```java
// El bridge acepta cualquier método por nombre + args como JSON array
// Ejemplo: {"method": "ManejoProductos_exportarProductosExcel_Sincronizar", "args": [1]}
Object result = rmiServer.metodoGeneral(methodName, argsArray);
// El result puede ser: BeanVectorTabla, BigDecimal, String, ParametrosResultadoMetodo, etc.
// encodeResult() lo serializa a JSON
```

### 3.4 Compilar y construir el JAR

```bash
cd /path/to/celeste-bridge
npm run build-bridge
# equivale a:
javac -proc:none \
  -cp '/Library/Celeste/Cliente/CelesteLanzador.jar:/Library/Celeste/Cliente/recursos/produccion/CelesteMipyme.jar' \
  CelesteJavaBridge.java
jar cf CelesteJavaBridge.jar CelesteJavaBridge*.class
```

---

## Fase 4 — Exponer como API HTTP (Node.js + Cloud Run)

### 4.1 celeste-api.js — wrappers de alto nivel

```js
// Cada operación es una función que:
// 1. Asegura que el bridge esté corriendo y con sesión activa
// 2. Llama al método RMI vía POST /call
// 3. Transforma la respuesta tabular en JSON limpio

async function buscarProductos(q) {
  // a) Catálogo desde export (cacheado 5 min) para filtrar por nombre/PLU
  const exportRows = await callMethod('ManejoProductos_exportarProductosExcel_Sincronizar', [1])
  // b) Stock real en paralelo: getFisicoBodega(codigoInterno, bodegaId)
  const stocks = await Promise.all(matched.map(r => _getFisicoBodega(r[0], bodegaId)))
  // c) Armar respuesta con 11 columnas confirmadas
}
```

### 4.2 server.js — HTTP server Express para Cloud Run

```js
app.get('/productos', async (req, res) => {
  const result = await api.buscarProductos(req.query.q)
  res.json(result)
})
```

### 4.3 Dockerfile para Cloud Run

```dockerfile
FROM node:20-slim
# Java runtime (para el bridge)
RUN apt-get install -y default-jre-headless
# Copiar JARs del cliente (deben ir en el build context)
COPY lib/ /app/lib/
COPY CelesteJavaBridge.jar /app/
COPY package*.json /app/
RUN npm ci --omit=dev
CMD ["node", "server.js"]
```

### 4.4 Deploy a Cloud Run

```bash
gcloud run deploy celeste-bridge \
  --source . \
  --project megasalud-backend \
  --region us-east1 \
  --allow-unauthenticated        # público para que Firebase Functions lo llame sin token
  # O --no-allow-unauthenticated + IAM binding para llamadas autenticadas

# Si se desplegó sin --allow-unauthenticated y quieres hacerlo público después:
gcloud run services add-iam-policy-binding celeste-bridge \
  --project megasalud-backend \
  --region us-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

---

## Fase 5 — Descubrir nuevos métodos en producción

Una vez el bridge está corriendo, el flujo para agregar un nuevo método es:

```
1. Identificar la necesidad
   "Necesito saber el precio de lista 2 de un producto"

2. Buscar en bytecode
   strings /tmp/celeste_extract/productos/manejo/ManejoProductos.class | grep -i "precio\|lista"
   → ManejoProductos_getPreciosLista_Sincronizar

3. Probar directamente con /call
   curl localhost:9191/call -d '{"method":"ManejoProductos_getPreciosLista_Sincronizar","args":[3745]}'

4. Si retorna datos: agregar wrapper en celeste-api.js + endpoint en server.js
5. Si retorna NULL: el método requiere args complejos → buscar variante _Sincronizar con primitivos

6. Compilar JAR solo si se modificó CelesteJavaBridge.java
   npm run build-bridge

7. Deploy
   gcloud run deploy celeste-bridge --source . --project megasalud-backend --region us-east1
```

---

## Datos clave de Celeste (referencia rápida)

| Dato | Valor |
|---|---|
| RMI URL | `//134.209.69.212:1133/SME-Produccion-C3-Publica` |
| bodegaId | `3` (de `otrosDatos[5]` del login, también en `/health`) |
| empresaId | `508` |
| empresaIdWSC | `754029` |
| Cloud Run URL | `https://celeste-bridge-143096173578.us-east1.run.app` |
| Firebase Functions URL | `https://us-east1-megasalud-backend.cloudfunctions.net/api` |

### Métodos confirmados que funcionan

| Método RMI | Args | Retorna | Uso |
|---|---|---|---|
| `ManejoProductos_exportarProductosExcel_Sincronizar` | `[1]` | `BeanVectorTabla` (19 cols) | Catálogo completo (sin stock) |
| `ManejoProductosBusquedas_getFisicoBodega` | `[codigoInterno: Int, bodegaId: Int]` | `BigDecimal` | Stock físico real |
| `ManejoTerceros_AutocompletadoTerceros` | `[query: String, "ENUM:CLIENTE"]` | autocomplete JSON | Buscar cliente |
| `ManejoTerceros_getDatosTercero_ConID` | `[id: Int]` | JSON cliente | Cliente por ID |

### Métodos que NO funcionan vía bridge

| Método | Por qué |
|---|---|
| `ManejoProductos_BusquedaPrimariaProductos` | `vectorReemplazosSQL` es `transient` → servidor recibe placeholder literal |
| `ManejoInventario_consultarStock_Sincronizar` | Requiere sesión GUI con bodega seleccionada |

---

## Aplicación a otras apps

Para replicar esta metodología con otra app de escritorio:

1. **Interceptar** con mitmproxy (HTTP/S) o Wireshark (TCP binario)
2. **Identificar el protocolo**: HTTP/REST, RMI, SOAP, protocolo propietario binario
3. **Localizar los JARs / DLLs** que implementan el cliente del protocolo
4. **Construir el bridge** en el mismo lenguaje que la app cliente (Java → Java bridge, .NET → C# bridge)
5. **Reutilizar las clases de serialización** del cliente original — no reinventar el protocolo
6. **Exponer HTTP** con un servidor ligero (Express, Flask, Actix, etc.)
7. **Desplegar en Cloud Run** para que el resto del stack pueda consumirlo

La clave es **no intentar reimplementar el protocolo desde cero**: en cambio, cargar las librerías del cliente original en el proceso del bridge y dejar que ellas hablen con el servidor. El bridge solo traduce HTTP → llamadas nativas de la app.

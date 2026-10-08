/**
 * AP-0035 — pre-compresión del bundle estático.
 *
 * Tras `vite build`, recorre `dist/` y genera, junto a cada asset compresible que
 * supere el umbral, una variante `.br` (Brotli, calidad 11) y `.gz` (gzip, nivel 9).
 * El host estático/edge sirve el pre-comprimido (Content-Encoding) sin recomprimir
 * en cada request.
 *
 * Usa SOLO la stdlib de Node (node:zlib incluye Brotli y gzip) — sin dependencias.
 */
import { readdirSync, statSync, readFileSync, writeFileSync } from 'node:fs';
import { join, extname } from 'node:path';
import { gzipSync, brotliCompressSync, constants } from 'node:zlib';

const DIST = 'dist';
const UMBRAL_BYTES = 500; // alineado con compress_minimum_size del backend
const EXTENSIONES = new Set(['.js', '.mjs', '.css', '.html', '.svg', '.json', '.xml', '.txt', '.wasm']);

/** Recoge recursivamente los ficheros bajo un directorio. */
function listarFicheros(dir) {
  const salida = [];
  for (const entrada of readdirSync(dir)) {
    const ruta = join(dir, entrada);
    const info = statSync(ruta);
    if (info.isDirectory()) salida.push(...listarFicheros(ruta));
    else salida.push(ruta);
  }
  return salida;
}

function comprimir() {
  let comprimidos = 0;
  let ahorroBr = 0;
  let original = 0;

  for (const ruta of listarFicheros(DIST)) {
    const ext = extname(ruta).toLowerCase();
    if (!EXTENSIONES.has(ext)) continue;
    if (ext === '.br' || ext === '.gz') continue;

    const datos = readFileSync(ruta);
    if (datos.length < UMBRAL_BYTES) continue;

    const br = brotliCompressSync(datos, {
      params: {
        [constants.BROTLI_PARAM_QUALITY]: 11,
        [constants.BROTLI_PARAM_SIZE_HINT]: datos.length,
      },
    });
    const gz = gzipSync(datos, { level: 9 });

    writeFileSync(`${ruta}.br`, br);
    writeFileSync(`${ruta}.gz`, gz);

    comprimidos += 1;
    original += datos.length;
    ahorroBr += datos.length - br.length;
  }

  const pct = original > 0 ? ((100 * ahorroBr) / original).toFixed(1) : '0.0';
  console.log(
    `[compress-dist] ${comprimidos} ficheros -> .br + .gz | ` +
      `original ${(original / 1024).toFixed(1)} KB, ahorro brotli ${(ahorroBr / 1024).toFixed(1)} KB (${pct}%)`,
  );
}

comprimir();

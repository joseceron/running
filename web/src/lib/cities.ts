/**
 * Catálogo de ciudades con altitud (msnm).
 *
 * Usado en el onboarding para auto-rellenar `altitude_msnm` cuando el user
 * elige su ciudad. Si la ciudad no está, el form muestra input manual.
 *
 * Fuente: GeoNames + Wikipedia. Mantén ordenado por país → ciudad.
 */

export type CityOption = {
  /** Nombre canónico para guardar en `runner_profile.city` */
  name: string;
  /** Etiqueta visible (incluye país para desambiguar) */
  label: string;
  /** Altitud media en metros sobre el nivel del mar */
  altitude_msnm: number;
};

export const CITIES: CityOption[] = [
  // Colombia
  { name: "Bogotá", label: "Bogotá · Colombia", altitude_msnm: 2640 },
  { name: "Medellín", label: "Medellín · Colombia", altitude_msnm: 1495 },
  { name: "Cali", label: "Cali · Colombia", altitude_msnm: 995 },
  { name: "Barranquilla", label: "Barranquilla · Colombia", altitude_msnm: 18 },
  { name: "Cartagena", label: "Cartagena · Colombia", altitude_msnm: 2 },
  { name: "Popayán", label: "Popayán · Colombia", altitude_msnm: 1736 },
  { name: "Bucaramanga", label: "Bucaramanga · Colombia", altitude_msnm: 959 },
  { name: "Pereira", label: "Pereira · Colombia", altitude_msnm: 1411 },
  { name: "Manizales", label: "Manizales · Colombia", altitude_msnm: 2150 },
  // México
  { name: "Ciudad de México", label: "CDMX · México", altitude_msnm: 2240 },
  { name: "Guadalajara", label: "Guadalajara · México", altitude_msnm: 1566 },
  { name: "Monterrey", label: "Monterrey · México", altitude_msnm: 540 },
  // Argentina
  { name: "Buenos Aires", label: "Buenos Aires · Argentina", altitude_msnm: 25 },
  { name: "Córdoba", label: "Córdoba · Argentina", altitude_msnm: 360 },
  { name: "Mendoza", label: "Mendoza · Argentina", altitude_msnm: 746 },
  // Perú
  { name: "Lima", label: "Lima · Perú", altitude_msnm: 154 },
  { name: "Cusco", label: "Cusco · Perú", altitude_msnm: 3399 },
  // Chile
  { name: "Santiago de Chile", label: "Santiago · Chile", altitude_msnm: 567 },
  // Ecuador
  { name: "Quito", label: "Quito · Ecuador", altitude_msnm: 2850 },
  { name: "Guayaquil", label: "Guayaquil · Ecuador", altitude_msnm: 4 },
  // Otros
  { name: "Caracas", label: "Caracas · Venezuela", altitude_msnm: 900 },
  { name: "La Paz", label: "La Paz · Bolivia", altitude_msnm: 3640 },
  { name: "Madrid", label: "Madrid · España", altitude_msnm: 667 },
  { name: "Barcelona", label: "Barcelona · España", altitude_msnm: 12 },
  { name: "Miami", label: "Miami · EE.UU.", altitude_msnm: 2 },
];

/** Busca por nombre exacto (case-insensitive). */
export function findCity(name: string): CityOption | undefined {
  const n = name.trim().toLowerCase();
  return CITIES.find((c) => c.name.toLowerCase() === n);
}

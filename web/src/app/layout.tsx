import type { Metadata } from "next";
import { Instrument_Serif, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Liebre — Tu pacer con inteligencia artificial",
  description:
    "Análisis biomecánico real de Garmin + literatura científica para correr seguro. Plan adaptativo basado en tu baseline personal, no en rangos genéricos.",
  metadataBase: new URL("https://liebre.run"),
  openGraph: {
    title: "Liebre — Corre seguro con IA + ciencia",
    description:
      "Tu liebre personal: agente IA que analiza tus datos Garmin y respalda cada recomendación con papers científicos.",
    type: "website",
    locale: "es_CO",
    url: "https://liebre.run",
    siteName: "Liebre",
  },
  alternates: {
    canonical: "https://liebre.run",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es-CO"
      className={`${inter.variable} ${instrumentSerif.variable} ${jetbrains.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-paper text-ink">{children}</body>
    </html>
  );
}

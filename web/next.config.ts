import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // SSR habilitado (NO output: "export") — necesario para dashboard auth-gated
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

import type { NextConfig } from "next";
const config: NextConfig = {
  output: "standalone",
  allowedDevOrigins: process.env.RALLYSENSE_DEV_ORIGIN
    ? [process.env.RALLYSENSE_DEV_ORIGIN]
    : [],
};
export default config;

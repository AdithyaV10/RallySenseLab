import next from "eslint-config-next/core-web-vitals";
import ts from "eslint-config-next/typescript";
const config = [
  ...next,
  ...ts,
  {
    ignores: [
      ".next/**",
      "public/vendor/**",
      "src/lib/schema.d.ts",
      "next-env.d.ts",
      "test-results/**",
      "playwright-report/**",
    ],
  },
];
export default config;

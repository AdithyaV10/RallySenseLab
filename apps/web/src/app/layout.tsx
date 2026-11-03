import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";
export const metadata: Metadata = {
  title: "RallySense Lab · Movement intelligence",
  description:
    "A workspace for synchronized movement observations, inertial signals, and reproducible research.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

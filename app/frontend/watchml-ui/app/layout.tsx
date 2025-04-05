import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WatchML - Machine Learning for your Apple Watch",
  description: "Machine Learning for your Apple Watch",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Link href="/">Home</Link>
        {children}
      </body>
    </html>
  );
}

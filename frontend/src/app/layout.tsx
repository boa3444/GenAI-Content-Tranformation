import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Content Transformation Engine",
  description: "Studio Light Minimal Content Transformation Platform with BM25 + FAISS Hybrid Retrieval & Remotion Video Generator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className="bg-white text-[#0A0A0A] antialiased min-h-screen relative overflow-x-hidden selection:bg-[#0A0A0A] selection:text-white">
        <main className="relative z-10 min-h-screen flex flex-col">{children}</main>
      </body>
    </html>
  );
}

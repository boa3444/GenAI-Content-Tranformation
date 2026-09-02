import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Content Transformation Engine",
  description: "Enterprise Hub-and-Spoke Content Transformation Platform with BM25 + FAISS Hybrid Retrieval & Remotion Video Generator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-800 antialiased min-h-screen relative overflow-x-hidden selection:bg-blue-100 selection:text-blue-900">
        <main className="relative z-10 min-h-screen flex flex-col">{children}</main>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { NextAuthProvider } from "@/providers/NextAuthProvider";
import Navigation from "@/components/layout/Navigation";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ReplyMint - AI-Powered Email Auto-Replies",
  description: "Automate your email responses with AI-powered auto-replies. Save time and never miss important emails.",
  keywords: ["email automation", "AI", "productivity", "business", "communication"],
  authors: [{ name: "ReplyMint Team" }],
  creator: "ReplyMint",
  publisher: "ReplyMint",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: "ReplyMint - AI-Powered Email Auto-Replies",
    description: "Automate your email responses with AI-powered auto-replies. Save time and never miss important emails.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ReplyMint - AI-Powered Email Auto-Replies",
    description: "Automate your email responses with AI-powered auto-replies. Save time and never miss important emails.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50`}
      >
        <NextAuthProvider>
          <Navigation />
          <main className="min-h-screen">{children}</main>
        </NextAuthProvider>
      </body>
    </html>
  );
}

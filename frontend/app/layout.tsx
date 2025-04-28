import type React from "react"
import type { Metadata } from "next"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import ScrollToTop from "@/components/scroll-to-top"
import { Auth0ProviderWithNavigate } from "@/components/auth/auth0-provider"

// Remplacer Open Sans par Lato
import { Lato, Inter } from "next/font/google"

// Configurer la police Lato avec preload: true
const lato = Lato({
  subsets: ["latin"],
  weight: ["100", "300", "400", "700", "900"],
  display: "swap",
  variable: "--font-lato",
  preload: true,
})

// Configurer la police Inter pour les interfaces SaaS modernes avec preload: true
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
  preload: true,
})

export const metadata: Metadata = {
  title: "BerinIA - Solutions d'automatisation IA",
  description: "BerinIA transforme votre service client avec des solutions d'IA avancées",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="fr" suppressHydrationWarning className={`${lato.variable} ${inter.variable} overflow-x-hidden`}>
      <head>
        {/* Ajouter une balise meta pour s'assurer que le type MIME est correct */}
        <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
      </head>
      <body className="font-lato overflow-x-hidden max-w-[100vw]">
        <Auth0ProviderWithNavigate>
          <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
            <ScrollToTop />
            <div className="flex flex-col min-h-screen w-full overflow-x-hidden max-w-[100vw]">{children}</div>
          </ThemeProvider>
        </Auth0ProviderWithNavigate>
      </body>
    </html>
  )
}

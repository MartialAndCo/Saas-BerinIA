"use client"

import { useEffect } from "react"
import { usePathname } from "next/navigation"

export default function ScrollToTop() {
  const pathname = usePathname()

  useEffect(() => {
    // Remonter en haut de la page lors du changement de route
    window.scrollTo(0, 0)
  }, [pathname])

  return null
}

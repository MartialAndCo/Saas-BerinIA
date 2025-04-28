"use client"

import type React from "react"

import { useRouter } from "next/navigation"
import Link from "next/link"
import type { LinkProps } from "next/link"
import type { ReactNode } from "react"

interface ScrollToTopLinkProps extends LinkProps {
  children: ReactNode
  className?: string
}

export default function ScrollToTopLink({ children, className, href, ...props }: ScrollToTopLinkProps) {
  const router = useRouter()

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()

    // Naviguer vers la nouvelle page
    router.push(href.toString())

    // Remonter en haut de la page
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  }

  return (
    <Link href={href} {...props} onClick={handleClick} className={className}>
      {children}
    </Link>
  )
}

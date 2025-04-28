"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

interface TypewriterHeadlineProps {
  prefix?: string
  variations: string[]
  speed?: number
  delay?: number
  className?: string
  prefixClassName?: string
  typingClassName?: string
}

export default function TypewriterHeadline({
  prefix = "",
  variations,
  speed = 100,
  delay = 2000,
  className = "",
  prefixClassName = "",
  typingClassName = "",
}: TypewriterHeadlineProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [displayText, setDisplayText] = useState("")
  const [isTyping, setIsTyping] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (!variations.length) return

    let timer: NodeJS.Timeout

    if (isPaused) {
      timer = setTimeout(() => {
        setIsPaused(false)
        setIsDeleting(true)
      }, delay)
      return () => clearTimeout(timer)
    }

    if (isDeleting) {
      if (displayText.length === 0) {
        setIsDeleting(false)
        setCurrentIndex((prev) => (prev + 1) % variations.length)
        return
      }

      timer = setTimeout(() => {
        setDisplayText((prev) => prev.slice(0, -1))
      }, speed / 2)
      return () => clearTimeout(timer)
    }

    if (isTyping) {
      const currentVariation = variations[currentIndex]
      if (displayText.length < currentVariation.length) {
        timer = setTimeout(() => {
          setDisplayText(currentVariation.slice(0, displayText.length + 1))
        }, speed)
      } else {
        setIsTyping(false)
        setIsPaused(true)
      }
    }

    return () => clearTimeout(timer)
  }, [currentIndex, delay, displayText, isDeleting, isPaused, isTyping, speed, variations])

  return (
    <div className={cn("flex flex-col", className)}>
      {prefix && <span className={cn("block", prefixClassName)}>{prefix}</span>}
      <div className={cn("flex items-center", typingClassName)}>
        <span>{displayText}</span>
        <span className="inline-block w-[2px] h-[1em] bg-current animate-pulse ml-0.5"></span>
      </div>
    </div>
  )
}

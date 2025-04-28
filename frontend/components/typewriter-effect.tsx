"use client"

import { useState, useEffect } from "react"

interface TypewriterEffectProps {
  text: string
  speed?: number
  delay?: number
  className?: string
}

export default function TypewriterEffect({ text, speed = 100, delay = 1000, className = "" }: TypewriterEffectProps) {
  const [displayText, setDisplayText] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)

  useEffect(() => {
    let timer: NodeJS.Timeout

    if (isWaiting) {
      timer = setTimeout(() => {
        setIsWaiting(false)
        setIsDeleting(true)
      }, delay)
      return () => clearTimeout(timer)
    }

    if (isDeleting) {
      if (displayText.length === 0) {
        setIsDeleting(false)
        return
      }

      timer = setTimeout(() => {
        setDisplayText((prev) => prev.slice(0, -1))
      }, speed / 2)
      return () => clearTimeout(timer)
    }

    if (currentIndex < text.length) {
      timer = setTimeout(() => {
        setDisplayText((prev) => prev + text[currentIndex])
        setCurrentIndex((prev) => prev + 1)
      }, speed)
    } else {
      setIsWaiting(true)
    }

    return () => clearTimeout(timer)
  }, [currentIndex, delay, displayText, isDeleting, isWaiting, speed, text])

  return (
    <span className={className}>
      {displayText}
      <span className="animate-pulse">|</span>
    </span>
  )
}

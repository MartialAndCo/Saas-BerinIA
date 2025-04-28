"use client"

import { useEffect, useRef } from "react"

export default function AnimatedGradient() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let width = window.innerWidth
    let height = window.innerHeight

    const resizeCanvas = () => {
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width
      canvas.height = height
    }

    window.addEventListener("resize", resizeCanvas)
    resizeCanvas()

    // Create gradient circles
    const circles = [
      { x: width * 0.2, y: height * 0.3, radius: 300, color: "rgba(147, 51, 234, 0.15)", speed: 0.0005 },
      { x: width * 0.8, y: height * 0.7, radius: 250, color: "rgba(59, 130, 246, 0.15)", speed: 0.0007 },
      { x: width * 0.5, y: height * 0.2, radius: 200, color: "rgba(236, 72, 153, 0.1)", speed: 0.0009 },
    ]

    let animationFrameId: number
    let time = 0

    const animate = () => {
      ctx.clearRect(0, 0, width, height)

      // Update circle positions with gentle sine wave motion
      circles.forEach((circle) => {
        const newX = circle.x + Math.sin(time * circle.speed * 10) * 50
        const newY = circle.y + Math.cos(time * circle.speed * 15) * 30

        const gradient = ctx.createRadialGradient(newX, newY, 0, newX, newY, circle.radius)

        gradient.addColorStop(0, circle.color)
        gradient.addColorStop(1, "rgba(255, 255, 255, 0)")

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(newX, newY, circle.radius, 0, Math.PI * 2)
        ctx.fill()
      })

      time += 1
      animationFrameId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full -z-10" aria-hidden="true" />
}

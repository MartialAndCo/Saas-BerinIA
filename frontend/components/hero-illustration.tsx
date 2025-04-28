"use client"

import { useEffect, useRef } from "react"
import { Phone, Zap, Brain, MessageSquare, BarChart3 } from "lucide-react"

export default function HeroIllustration() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const setCanvasDimensions = () => {
      const parentWidth = canvas.parentElement?.clientWidth || 600
      const parentHeight = canvas.parentElement?.clientHeight || 500

      // Set display size (css pixels)
      canvas.style.width = parentWidth + "px"
      canvas.style.height = parentHeight + "px"

      // Set actual size in memory (scaled for retina)
      const dpr = window.devicePixelRatio || 1
      canvas.width = parentWidth * dpr
      canvas.height = parentHeight * dpr

      // Scale context to match the device pixel ratio
      ctx.scale(dpr, dpr)

      return { width: parentWidth, height: parentHeight }
    }

    const { width, height } = setCanvasDimensions()

    // Create nodes for network visualization
    const nodes: Node[] = []
    const numNodes = 50

    interface Node {
      x: number
      y: number
      radius: number
      color: string
      vx: number
      vy: number
      connected: boolean
      pulse: number
      pulseDirection: number
    }

    // Create nodes
    for (let i = 0; i < numNodes; i++) {
      const radius = Math.random() * 3 + 1.5
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius,
        color: i % 4 === 0 ? "#9333ea" : i % 4 === 1 ? "#3b82f6" : i % 4 === 2 ? "#6366f1" : "#8b5cf6",
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        connected: false,
        pulse: Math.random(),
        pulseDirection: Math.random() > 0.5 ? 1 : -1,
      })
    }

    // Add central nodes representing AI features
    const centralNodes = [
      {
        x: width * 0.5,
        y: height * 0.4,
        radius: 12,
        color: "#9333ea",
        vx: 0,
        vy: 0,
        connected: true,
        pulse: 0,
        pulseDirection: 1,
      }, // Chatbot
      {
        x: width * 0.3,
        y: height * 0.6,
        radius: 10,
        color: "#3b82f6",
        vx: 0,
        vy: 0,
        connected: true,
        pulse: 0.3,
        pulseDirection: 1,
      }, // Phone
      {
        x: width * 0.7,
        y: height * 0.7,
        radius: 10,
        color: "#6366f1",
        vx: 0,
        vy: 0,
        connected: true,
        pulse: 0.6,
        pulseDirection: 1,
      }, // Automation
    ]

    nodes.push(...centralNodes)

    // Draw function
    const draw = () => {
      ctx.clearRect(0, 0, width, height)

      // Draw connections
      ctx.lineWidth = 0.5

      for (let i = 0; i < nodes.length; i++) {
        const nodeA = nodes[i]

        // Connect to central nodes
        for (let j = nodes.length - centralNodes.length; j < nodes.length; j++) {
          const nodeB = nodes[j]
          const dx = nodeB.x - nodeA.x
          const dy = nodeB.y - nodeA.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 180) {
            const opacity = (1 - distance / 180) * 0.3
            const gradient = ctx.createLinearGradient(nodeA.x, nodeA.y, nodeB.x, nodeB.y)
            gradient.addColorStop(
              0,
              `${nodeA.color}${Math.floor(opacity * 255)
                .toString(16)
                .padStart(2, "0")}`,
            )
            gradient.addColorStop(
              1,
              `${nodeB.color}${Math.floor(opacity * 255)
                .toString(16)
                .padStart(2, "0")}`,
            )

            ctx.strokeStyle = gradient
            ctx.beginPath()
            ctx.moveTo(nodeA.x, nodeA.y)
            ctx.lineTo(nodeB.x, nodeB.y)
            ctx.stroke()
          }
        }

        // Connect to nearby nodes
        for (let j = i + 1; j < nodes.length - centralNodes.length; j++) {
          const nodeB = nodes[j]
          const dx = nodeB.x - nodeA.x
          const dy = nodeB.y - nodeA.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 80) {
            const opacity = (1 - distance / 80) * 0.2
            const gradient = ctx.createLinearGradient(nodeA.x, nodeA.y, nodeB.x, nodeB.y)
            gradient.addColorStop(
              0,
              `${nodeA.color}${Math.floor(opacity * 255)
                .toString(16)
                .padStart(2, "0")}`,
            )
            gradient.addColorStop(
              1,
              `${nodeB.color}${Math.floor(opacity * 255)
                .toString(16)
                .padStart(2, "0")}`,
            )

            ctx.strokeStyle = gradient
            ctx.beginPath()
            ctx.moveTo(nodeA.x, nodeA.y)
            ctx.lineTo(nodeB.x, nodeB.y)
            ctx.stroke()
          }
        }
      }

      // Draw nodes
      for (const node of nodes) {
        // Update pulse
        node.pulse += 0.01 * node.pulseDirection
        if (node.pulse > 1 || node.pulse < 0) {
          node.pulseDirection *= -1
        }

        // Draw node
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2)
        ctx.fillStyle = node.color
        ctx.fill()

        // Draw glow for central nodes
        if (node.connected) {
          ctx.beginPath()
          const glowRadius = node.radius + 5 + node.pulse * 3
          ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2)
          const gradient = ctx.createRadialGradient(node.x, node.y, node.radius, node.x, node.y, glowRadius + 5)
          gradient.addColorStop(0, `${node.color}80`)
          gradient.addColorStop(1, `${node.color}00`)
          ctx.fillStyle = gradient
          ctx.fill()
        }
      }
    }

    // Update function
    const update = () => {
      for (let i = 0; i < nodes.length - centralNodes.length; i++) {
        const node = nodes[i]

        // Update position
        node.x += node.vx
        node.y += node.vy

        // Bounce off edges
        if (node.x < node.radius || node.x > width - node.radius) {
          node.vx *= -1
        }

        if (node.y < node.radius || node.y > height - node.radius) {
          node.vy *= -1
        }

        // Keep within bounds
        node.x = Math.max(node.radius, Math.min(width - node.radius, node.x))
        node.y = Math.max(node.radius, Math.min(height - node.radius, node.y))
      }
    }

    // Animation loop
    let animationFrameId: number

    const animate = () => {
      update()
      draw()
      animationFrameId = requestAnimationFrame(animate)
    }

    // Handle resize
    const handleResize = () => {
      const { width: newWidth, height: newHeight } = setCanvasDimensions()

      // Adjust node positions
      for (const node of nodes) {
        node.x = (node.x / width) * newWidth
        node.y = (node.y / height) * newHeight
      }

      // Update central nodes
      if (centralNodes.length >= 3) {
        centralNodes[0].x = newWidth * 0.5
        centralNodes[0].y = newHeight * 0.4
        centralNodes[1].x = newWidth * 0.3
        centralNodes[1].y = newHeight * 0.6
        centralNodes[2].x = newWidth * 0.7
        centralNodes[2].y = newHeight * 0.7
      }
    }

    window.addEventListener("resize", handleResize)
    animate()

    return () => {
      window.removeEventListener("resize", handleResize)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <div className="relative w-full h-[500px] bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-700">
      <canvas ref={canvasRef} className="w-full h-full" />

      {/* Overlay elements with improved design */}
      <div className="absolute top-1/4 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-purple-200 dark:border-purple-800 transition-all duration-300 hover:scale-105">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center shadow-md">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-lg">Chatbot IA</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Réponses instantanées 24/7</div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-1/4 left-1/4 transform -translate-x-1/2 translate-y-1/2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-blue-200 dark:border-blue-800 transition-all duration-300 hover:scale-105">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-md">
            <Phone className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-lg">Standard IA</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Routage intelligent des appels</div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-1/3 right-1/4 transform translate-x-1/2 translate-y-1/2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-indigo-200 dark:border-indigo-800 transition-all duration-300 hover:scale-105">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-md">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-lg">Automatisation</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Processus optimisés</div>
          </div>
        </div>
      </div>

      {/* Floating elements for added visual interest */}
      <div className="absolute top-1/2 right-1/6 transform rotate-12 opacity-80">
        <MessageSquare className="h-8 w-8 text-purple-400 dark:text-purple-500 animate-pulse" />
      </div>

      <div className="absolute bottom-1/6 left-1/3 transform -rotate-6 opacity-80">
        <BarChart3 className="h-8 w-8 text-blue-400 dark:text-blue-500 animate-float" />
      </div>
    </div>
  )
}

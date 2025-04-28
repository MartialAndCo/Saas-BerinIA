"use client"

import { useEffect, useState, useRef } from "react"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { useMediaQuery } from "@/hooks/use-media-query"

// Supprimer ou commenter les données fictives
// const data = [
//   { date: "1 Mai", conversion: 4.0 },
//   { date: "5 Mai", conversion: 4.2 },
//   ...
// ]

interface ConversionChartProps {
  data: any[];
}

export function ConversionChart({ data }: ConversionChartProps) {
  const [isMounted, setIsMounted] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const isMobile = useMediaQuery("(max-width: 768px)")

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return <div className="h-[300px] flex items-center justify-center">Chargement du graphique...</div>
  }

  return (
    <div ref={containerRef} className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 20,
            right: isMobile ? 10 : 20,
            bottom: 20,
            left: isMobile ? 0 : 10,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="date"
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            tickMargin={isMobile ? 5 : 10}
          />
          <YAxis
            domain={[0, 10]}
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            tickMargin={isMobile ? 5 : 10}
            width={isMobile ? 30 : 40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--background))",
              borderColor: "hsl(var(--border))",
              borderRadius: "var(--radius)",
              fontSize: isMobile ? 10 : 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="conversion"
            name="Taux de conversion (%)"
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            dot={{ r: isMobile ? 3 : 4 }}
            activeDot={{ r: isMobile ? 5 : 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

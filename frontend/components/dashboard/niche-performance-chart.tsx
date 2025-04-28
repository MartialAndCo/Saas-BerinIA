"use client"

import { useEffect, useState, useRef } from "react"
import { Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart } from "recharts"
import { useMediaQuery } from "@/hooks/use-media-query"

const data = [
  { name: "Immobilier", conversion: 7.8, cpl: 1.85 },
  { name: "Juridique", conversion: 5.2, cpl: 2.1 },
  { name: "Architecture", conversion: 9.1, cpl: 1.65 },
  { name: "RH", conversion: 3.2, cpl: 3.45 },
  { name: "Santé", conversion: 6.5, cpl: 2.25 },
  { name: "Restauration", conversion: 4.8, cpl: 2.75 },
  { name: "Éducation", conversion: 2.3, cpl: 4.85 },
  { name: "Tourisme", conversion: 2.1, cpl: 5.2 },
]

export function NichePerformanceChart() {
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
        <BarChart
          data={data}
          margin={{
            top: 20,
            right: isMobile ? 10 : 30,
            bottom: isMobile ? 10 : 5,
            left: isMobile ? 0 : 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="name"
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            tickMargin={isMobile ? 5 : 10}
            interval={0}
            angle={isMobile ? -45 : 0}
            textAnchor={isMobile ? "end" : "middle"}
            height={isMobile ? 60 : 30}
          />
          <YAxis
            yAxisId="left"
            orientation="left"
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            tickMargin={isMobile ? 5 : 10}
            width={isMobile ? 30 : 40}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 6]}
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
          <Legend wrapperStyle={{ fontSize: isMobile ? 10 : 12 }} iconSize={isMobile ? 8 : 10} />
          <Bar
            yAxisId="left"
            dataKey="conversion"
            name="Taux de conversion (%)"
            fill="hsl(var(--primary))"
            radius={[4, 4, 0, 0]}
            barSize={isMobile ? 15 : 20}
          />
          <Bar
            yAxisId="right"
            dataKey="cpl"
            name="Coût par lead (€)"
            fill="hsl(var(--destructive))"
            radius={[4, 4, 0, 0]}
            barSize={isMobile ? 15 : 20}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

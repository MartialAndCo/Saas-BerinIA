"use client"

import { useEffect, useState, useRef } from "react"
import { Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Line, ComposedChart } from "recharts"
import { useMediaQuery } from "@/hooks/use-media-query"

interface DashboardChartProps {
  className?: string;
  data: any[];
}

export function DashboardChart({ className, data }: DashboardChartProps) {
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
        <ComposedChart
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
            dataKey="name"
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            tickMargin={isMobile ? 5 : 10}
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
          <Legend wrapperStyle={{ fontSize: isMobile ? 10 : 12 }} iconSize={isMobile ? 8 : 10} />
          <Bar
            yAxisId="left"
            dataKey="leads"
            name="Leads collectés"
            fill="hsl(var(--primary))"
            radius={[4, 4, 0, 0]}
            barSize={isMobile ? 15 : 20}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="conversion"
            name="Taux de conversion (%)"
            stroke="hsl(var(--destructive))"
            strokeWidth={2}
            dot={{ r: isMobile ? 3 : 4 }}
            activeDot={{ r: isMobile ? 5 : 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

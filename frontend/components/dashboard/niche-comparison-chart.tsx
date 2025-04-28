"use client"

import { useEffect, useState, useRef } from "react"
import { Scatter, ScatterChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from "recharts"
import { useMediaQuery } from "@/hooks/use-media-query"

// Supprimer ou commenter les données fictives
// const data = [
//   { name: "Immobilier", conversion: 7.8, cpl: 1.85, leads: 440 },
//   { name: "Juridique", conversion: 5.2, cpl: 2.1, leads: 215 },
//   ...
// ]

interface NicheComparisonChartProps {
  data: any[];
}

export function NicheComparisonChart({ data }: NicheComparisonChartProps) {
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
        <ScatterChart
          margin={{
            top: 20,
            right: isMobile ? 10 : 20,
            bottom: isMobile ? 60 : 20,
            left: isMobile ? 10 : 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            type="number"
            dataKey="conversion"
            name="Taux de conversion"
            unit="%"
            domain={[0, 10]}
            label={{
              value: isMobile ? "Conv. (%)" : "Taux de conversion (%)",
              position: "bottom",
              className: "text-xs",
              offset: isMobile ? 0 : 5,
              dy: isMobile ? 20 : 10,
            }}
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
          />
          <YAxis
            type="number"
            dataKey="cpl"
            name="Coût par lead"
            unit="€"
            domain={[0, 6]}
            label={{
              value: isMobile ? "CPL (€)" : "Coût par lead (€)",
              angle: -90,
              position: "left",
              className: "text-xs",
              dx: isMobile ? -30 : -10,
            }}
            className="text-xs"
            tick={{ fontSize: isMobile ? 10 : 12 }}
            width={isMobile ? 40 : 60}
          />
          <ZAxis type="number" dataKey="leads" range={[50, 400]} name="Leads" />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{
              backgroundColor: "hsl(var(--background))",
              borderColor: "hsl(var(--border))",
              borderRadius: "var(--radius)",
              fontSize: isMobile ? 10 : 12,
            }}
            formatter={(value, name, props) => {
              if (name === "Coût par lead") return [`${value}€`, name]
              if (name === "Taux de conversion") return [`${value}%`, name]
              return [value, name]
            }}
          />
          <Scatter
            name="Niches"
            data={data}
            fill="hsl(var(--primary))"
            shape="circle"
            legendType="none"
            label={(props) => {
              const { x, y, width, height, value, index } = props
              return (
                <text
                  x={x + width / 2}
                  y={y - 10}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-[10px] fill-current"
                  fontSize={isMobile ? 8 : 10}
                >
                  {data[index].name}
                </text>
              )
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

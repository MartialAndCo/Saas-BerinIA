"use client"

import { useEffect, useState, useRef } from "react"
import { Bar, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { useMediaQuery } from "@/hooks/use-media-query"

// Supprimer ou commenter les données fictives
// const data = [
//   {
//     name: "Immobilier Paris",
//     leads: 342,
//     conversion: 7.8,
//   },
//   ...
// ]

interface CampaignComparisonChartProps {
  data: any[];
}

export function CampaignComparisonChart({ data }: CampaignComparisonChartProps) {
  const [isMounted, setIsMounted] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const isMobile = useMediaQuery("(max-width: 768px)")

  // Pour les écrans mobiles, réduisons les noms des campagnes
  const formattedData = isMobile
    ? data.map((item) => ({
        ...item,
        name: item.name.split(" ")[0], // Prendre seulement le premier mot
      }))
    : data

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
          data={formattedData}
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
            name="Leads"
            fill="#8884d8"
            radius={[4, 4, 0, 0]}
            barSize={isMobile ? 15 : 20}
          />
          <Bar
            yAxisId="right"
            dataKey="conversion"
            name="Conversion (%)"
            fill="#82ca9d"
            radius={[4, 4, 0, 0]}
            barSize={isMobile ? 15 : 20}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

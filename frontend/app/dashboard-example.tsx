"use client"

import { LayoutDashboard, Users, BarChart2, Calendar } from "lucide-react"
import DashboardButton from "@/components/dashboard-button"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function DashboardExample() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold mb-6">Exemples de style d'ombre</h1>

      {/* Exemple du bouton Dashboard comme dans l'image */}
      <DashboardButton href="#" icon={LayoutDashboard} label="Dashboard" active={true} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        {/* Variante avec le composant Button */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium">Avec le composant Button</h2>
          <Button variant="dashboard" size="dashboard" className="w-full justify-start">
            <LayoutDashboard className="mr-3 h-5 w-5" />
            Dashboard
          </Button>

          <Button variant="dashboard" size="dashboard" className="w-full justify-start">
            <Users className="mr-3 h-5 w-5" />
            Utilisateurs
          </Button>
        </div>

        {/* Variante avec le composant Card */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium">Avec le composant Card</h2>
          <Card className="p-4 flex items-center gap-3">
            <BarChart2 className="h-5 w-5 text-gray-500" />
            <span className="font-medium">Statistiques</span>
          </Card>

          <Card className="p-4 flex items-center gap-3">
            <Calendar className="h-5 w-5 text-gray-500" />
            <span className="font-medium">Calendrier</span>
          </Card>
        </div>
      </div>

      {/* Autres exemples de conteneurs avec cette ombre */}
      <div className="mt-8 space-y-4">
        <h2 className="text-lg font-medium">Autres exemples</h2>
        <div className="rounded-xl bg-white p-6 shadow-[0_0_10px_rgba(0,0,0,0.08)] border border-gray-100 dark:bg-gray-900 dark:border-gray-800 dark:shadow-[0_0_10px_rgba(0,0,0,0.15)]">
          <h3 className="text-lg font-medium mb-2">Conteneur personnalisé</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Ce conteneur utilise directement les classes Tailwind pour appliquer l'ombre uniforme.
          </p>
        </div>
      </div>
    </div>
  )
}

import { Bot, Calendar, Check, Clock, X } from "lucide-react"
import { cn } from "@/lib/utils"

const activities = [
  {
    id: 1,
    type: "agent",
    agent: "Scraper Agent",
    action: "a collecté 120 leads",
    target: "Agences immobilières Paris",
    time: "Il y a 5 minutes",
    status: "success",
  },
  {
    id: 2,
    type: "agent",
    agent: "Cleaner Agent",
    action: "a nettoyé 120 leads",
    target: "Agences immobilières Paris",
    time: "Il y a 12 minutes",
    status: "success",
  },
  {
    id: 3,
    type: "agent",
    agent: "Analytics Agent",
    action: "a rencontré une erreur",
    target: "API timeout",
    time: "Il y a 1 heure",
    status: "error",
  },
  {
    id: 4,
    type: "system",
    action: "Nouvelle campagne créée",
    target: "Consultants RH Lille",
    time: "Il y a 3 heures",
    status: "info",
  },
  {
    id: 5,
    type: "agent",
    agent: "Pivot Agent",
    action: "a recommandé de continuer",
    target: "Architectes Bordeaux",
    time: "Il y a 5 heures",
    status: "success",
  },
  {
    id: 6,
    type: "system",
    action: "Rapport hebdomadaire généré",
    target: "Semaine 22",
    time: "Il y a 1 jour",
    status: "info",
  },
]

// Ajouter cette interface
interface RecentActivityProps {
  className?: string;
  data: RecentActivityItem[];
}

// Puis modifier la définition du composant
export function RecentActivity({ className, data }: RecentActivityProps) {
  return (
    <div className="space-y-8">
      {data.map((activity) => (
        <div key={activity.id} className="flex items-start space-x-4">
          <div
            className={cn(
              "mt-0.5 rounded-full p-1",
              activity.status === "success" && "bg-green-100 dark:bg-green-900",
              activity.status === "error" && "bg-red-100 dark:bg-red-900",
              activity.status === "info" && "bg-blue-100 dark:bg-blue-900",
              activity.status === "warning" && "bg-yellow-100 dark:bg-yellow-900",
            )}
          >
            {activity.type === "agent" ? (
              <Bot
                className={cn(
                  "h-4 w-4",
                  activity.status === "success" && "text-green-600 dark:text-green-400",
                  activity.status === "error" && "text-red-600 dark:text-red-400",
                  activity.status === "info" && "text-blue-600 dark:text-blue-400",
                  activity.status === "warning" && "text-yellow-600 dark:text-yellow-400",
                )}
              />
            ) : activity.status === "success" ? (
              <Check className={cn("h-4 w-4", activity.status === "success" && "text-green-600 dark:text-green-400")} />
            ) : activity.status === "error" ? (
              <X className={cn("h-4 w-4", activity.status === "error" && "text-red-600 dark:text-red-400")} />
            ) : (
              <Calendar
                className={cn(
                  "h-4 w-4",
                  activity.status === "info" && "text-blue-600 dark:text-blue-400",
                  activity.status === "warning" && "text-yellow-600 dark:text-yellow-400",
                )}
              />
            )}
          </div>
          <div className="flex-1 space-y-1">
            <p className="text-sm font-medium leading-none">
              {activity.type === "agent" && <span>{activity.agent} </span>}
              {activity.action}
              {activity.target && <span className="font-semibold"> {activity.target}</span>}
            </p>
            <p className="flex items-center text-xs text-muted-foreground">
              <Clock className="mr-1 h-3 w-3" />
              {activity.time}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

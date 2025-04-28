/**
 * Composant d'état vide
 *
 * Ce composant est utilisé pour afficher un message lorsqu'aucune donnée n'est disponible,
 * avec une option pour afficher une action (comme un bouton pour créer un nouvel élément).
 */

import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

export function EmptyState({ icon, title, description, action, className = "" }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center bg-muted/30 border border-dashed border-muted rounded-lg",
        className,
      )}
    >
      {icon && <div className="mb-4 text-muted-foreground">{icon}</div>}

      <h3 className="text-lg font-medium">{title}</h3>

      {description && <p className="mt-2 text-sm text-muted-foreground max-w-md">{description}</p>}

      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}

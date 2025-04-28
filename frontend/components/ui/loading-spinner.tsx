/**
 * Composant de chargement
 *
 * Ce composant affiche un indicateur de chargement avec un texte optionnel.
 * Il peut être utilisé dans différentes tailles et avec différentes variantes.
 */

import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  text?: string
  fullPage?: boolean
  className?: string
  textClassName?: string
}

export function LoadingSpinner({
  size = "md",
  text,
  fullPage = false,
  className = "",
  textClassName = "",
}: LoadingSpinnerProps) {
  // Déterminer la taille du spinner
  const spinnerSize = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  }[size]

  // Composant de base
  const spinner = (
    <div className={cn("flex flex-col items-center justify-center", className)}>
      <Loader2 className={cn(spinnerSize, "animate-spin text-primary")} />
      {text && <p className={cn("mt-2 text-sm text-muted-foreground", textClassName)}>{text}</p>}
    </div>
  )

  // Si fullPage est true, on centre le spinner sur toute la page
  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}

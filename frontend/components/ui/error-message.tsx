"use client"

/**
 * Composant pour afficher un message d'erreur
 *
 * Ce composant est utilisé pour afficher des messages d'erreur de manière cohérente
 * dans toute l'application, avec une option pour afficher des détails supplémentaires.
 */

import { AlertCircle, X } from "lucide-react"
import { useState } from "react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

interface ErrorMessageProps {
  title?: string
  message: string
  details?: string
  onDismiss?: () => void
  className?: string
}

export function ErrorMessage({ title = "Erreur", message, details, onDismiss, className = "" }: ErrorMessageProps) {
  const [showDetails, setShowDetails] = useState(false)

  return (
    <Alert variant="destructive" className={`relative ${className}`}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>
        <p>{message}</p>

        {details && (
          <div className="mt-2">
            <Button
              variant="link"
              size="sm"
              className="p-0 h-auto text-destructive-foreground underline"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? "Masquer les détails" : "Afficher les détails"}
            </Button>

            {showDetails && (
              <pre className="mt-2 p-2 bg-destructive/20 rounded text-xs overflow-auto max-h-32">{details}</pre>
            )}
          </div>
        )}
      </AlertDescription>

      {onDismiss && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 h-6 w-6 text-destructive-foreground"
          onClick={onDismiss}
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Fermer</span>
        </Button>
      )}
    </Alert>
  )
}

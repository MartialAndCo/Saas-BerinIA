import { Check } from "lucide-react"
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface PricingCardProps {
  title: string
  price: string
  description: string
  features: string[]
  buttonText: string
  popular?: boolean
}

export default function PricingCard({
  title,
  price,
  description,
  features,
  buttonText,
  popular = false,
}: PricingCardProps) {
  return (
    <Card
      className={cn(
        "overflow-hidden border border-gray-200 dark:border-gray-800 transition-all duration-200 relative",
        popular ? "shadow-xl border-purple-200 dark:border-purple-900" : "hover:shadow-md",
      )}
    >
      {popular && (
        <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-600 to-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
          Populaire
        </div>
      )}

      <CardHeader className={cn("pb-0", popular ? "bg-purple-50 dark:bg-purple-900/20" : "")}>
        <h3 className="text-xl font-bold">{title}</h3>
        <div className="mt-2 mb-1">
          <span className="text-3xl font-bold">
            {price === "Sur mesure" ? "" : "€"}
            {price}
          </span>
          {price !== "Sur mesure" && <span className="text-gray-600 dark:text-gray-400">/mois</span>}
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{description}</p>
      </CardHeader>

      <CardContent className={cn("pt-6", popular ? "bg-purple-50 dark:bg-purple-900/20" : "")}>
        <ul className="space-y-3">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 text-green-500 mr-2 shrink-0" />
              <span className="text-gray-700 dark:text-gray-300 text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>

      <CardFooter className={cn("pt-4 pb-6", popular ? "bg-purple-50 dark:bg-purple-900/20" : "")}>
        <Button
          className={cn(
            "w-full",
            popular
              ? "bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600"
              : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700",
          )}
        >
          {buttonText}
        </Button>
      </CardFooter>
    </Card>
  )
}

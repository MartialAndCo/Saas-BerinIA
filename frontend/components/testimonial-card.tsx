import { Card, CardContent } from "@/components/ui/card"
import { QuoteIcon } from "lucide-react"

interface TestimonialCardProps {
  quote: string
  author: string
  company: string
  avatarUrl: string
}

export default function TestimonialCard({ quote, author, company, avatarUrl }: TestimonialCardProps) {
  return (
    <Card className="overflow-hidden border border-gray-200 dark:border-gray-800 transition-all duration-200 hover:shadow-md">
      <CardContent className="p-6">
        <QuoteIcon className="h-8 w-8 text-purple-200 dark:text-purple-900 mb-4" />
        <p className="text-gray-700 dark:text-gray-300 mb-6 italic">"{quote}"</p>
        <div className="flex items-center">
          <div className="h-10 w-10 rounded-full overflow-hidden mr-3">
            <img src={avatarUrl || "/placeholder.svg"} alt={author} className="h-full w-full object-cover" />
          </div>
          <div>
            <h4 className="font-medium">{author}</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">{company}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

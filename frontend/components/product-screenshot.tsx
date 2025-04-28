"use client"

import { useEffect, useState } from "react"
import { Bot, Phone, MessageSquare, BarChart3, Calendar, Users, CheckCircle2 } from "lucide-react"
import { Inter } from "next/font/google"

// Initialiser la police Inter pour une interface SaaS moderne
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
})

export default function ProductScreenshot() {
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    setLoaded(true)
  }, [])

  return (
    <div
      className={`relative w-full max-w-4xl mx-auto rounded-xl shadow-[0_0_15px_rgba(0,0,0,0.1)] dark:shadow-[0_0_15px_rgba(0,0,0,0.3)] overflow-hidden transition-all duration-1000 ${
        loaded ? "opacity-100 transform translate-y-0" : "opacity-0 transform translate-y-8"
      } ${inter.variable}`}
    >
      {/* Browser mockup */}
      <div className="bg-gray-100 dark:bg-gray-800 p-1 md:p-2 flex items-center">
        <div className="flex space-x-1 md:space-x-1.5 mr-2 md:mr-4">
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-red-500"></div>
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-yellow-500"></div>
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-green-500"></div>
        </div>
        <div className="flex-1 bg-white dark:bg-gray-700 h-4 md:h-6 rounded-md"></div>
      </div>

      {/* App interface */}
      <div className="bg-white dark:bg-gray-900 p-2 md:p-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4">
          {/* Sidebar - Hidden on mobile */}
          <div className="hidden md:block md:col-span-3 bg-gray-50 dark:bg-gray-800 rounded-lg p-3 md:p-4 shadow-[0_0_8px_rgba(0,0,0,0.05)] dark:shadow-[0_0_8px_rgba(0,0,0,0.15)]">
            <div className="flex items-center mb-4 md:mb-6">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center mr-2 md:mr-3 shadow-[0_0_4px_rgba(0,0,0,0.05)] dark:shadow-[0_0_4px_rgba(0,0,0,0.15)]">
                <span className="font-medium text-purple-600 dark:text-purple-300 text-xs md:text-sm">JD</span>
              </div>
              <div>
                <div className="font-medium font-inter tracking-tight text-sm md:text-base">Jean Dupont</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 font-inter">Responsable Service Client</div>
              </div>
            </div>

            <div className="space-y-1 md:space-y-2">
              <div className="flex items-center p-1.5 md:p-2 bg-purple-100 dark:bg-purple-900/30 rounded-md text-purple-600 dark:text-purple-300 shadow-[0_0_4px_rgba(0,0,0,0.03)] dark:shadow-[0_0_4px_rgba(0,0,0,0.1)]">
                <MessageSquare className="h-3 w-3 md:h-4 md:w-4 mr-2 md:mr-3" />
                <span className="text-xs md:text-sm font-medium font-inter tracking-tight">Conversations</span>
              </div>
              <div className="flex items-center p-1.5 md:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                <BarChart3 className="h-3 w-3 md:h-4 md:w-4 mr-2 md:mr-3 text-gray-500 dark:text-gray-400" />
                <span className="text-xs md:text-sm font-inter tracking-tight">Statistiques</span>
              </div>
              <div className="flex items-center p-1.5 md:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                <Calendar className="h-3 w-3 md:h-4 md:w-4 mr-2 md:mr-3 text-gray-500 dark:text-gray-400" />
                <span className="text-xs md:text-sm font-inter tracking-tight">Planification</span>
              </div>
              <div className="flex items-center p-1.5 md:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                <Users className="h-3 w-3 md:h-4 md:w-4 mr-2 md:mr-3 text-gray-500 dark:text-gray-400" />
                <span className="text-xs md:text-sm font-inter tracking-tight">Équipe</span>
              </div>
            </div>
          </div>

          {/* Main content - Full width on mobile */}
          <div className="col-span-1 md:col-span-9 space-y-2 md:space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-base md:text-xl font-bold font-inter tracking-tight">Tableau de bord IA</h2>
              <div className="flex items-center space-x-1 md:space-x-2">
                <div className="text-xs md:text-sm text-gray-500 dark:text-gray-400 font-inter hidden sm:block">
                  15% tâches
                </div>
                <div className="w-16 md:w-24 h-1.5 md:h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-[inset_0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[inset_0_0_3px_rgba(0,0,0,0.2)]">
                  <div className="h-full bg-purple-500 w-[15%]"></div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-4">
              <div className="bg-red-500 rounded-lg p-3 md:p-4 text-white shadow-[0_0_8px_rgba(0,0,0,0.08)] dark:shadow-[0_0_8px_rgba(0,0,0,0.2)]">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium font-inter tracking-tight text-sm md:text-base">Chatbot IA</h3>
                    <p className="text-xs md:text-sm text-red-100 mt-0.5 md:mt-1 font-inter">Configuration</p>
                  </div>
                  <Bot className="h-4 w-4 md:h-6 md:w-6" />
                </div>
                <div className="flex mt-2 md:mt-4 space-x-1">
                  <div className="w-4 h-4 md:w-6 md:h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] md:text-xs font-inter shadow-[0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    ML
                  </div>
                  <div className="w-4 h-4 md:w-6 md:h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] md:text-xs font-inter shadow-[0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    PD
                  </div>
                  <div className="w-4 h-4 md:w-6 md:h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] md:text-xs font-inter shadow-[0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    SB
                  </div>
                </div>
              </div>

              <div className="bg-purple-500 rounded-lg p-3 md:p-4 text-white shadow-[0_0_8px_rgba(0,0,0,0.08)] dark:shadow-[0_0_8px_rgba(0,0,0,0.2)]">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium font-inter tracking-tight text-sm md:text-base">Standard Tél.</h3>
                    <p className="text-xs md:text-sm text-purple-100 mt-0.5 md:mt-1 font-inter">Intégration</p>
                  </div>
                  <Phone className="h-4 w-4 md:h-6 md:w-6" />
                </div>
                <div className="flex mt-2 md:mt-4 space-x-1">
                  <div className="w-4 h-4 md:w-6 md:h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] md:text-xs font-inter shadow-[0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    JD
                  </div>
                  <div className="w-4 h-4 md:w-6 md:h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] md:text-xs font-inter shadow-[0_0_3px_rgba(0,0,0,0.05)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    ML
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 md:p-4 shadow-[0_0_8px_rgba(0,0,0,0.05)] dark:shadow-[0_0_8px_rgba(0,0,0,0.15)]">
              <div className="flex justify-between items-center mb-2 md:mb-4">
                <h3 className="font-medium font-inter tracking-tight text-sm md:text-base">Tâches en cours</h3>
                <div className="flex space-x-1 md:space-x-2">
                  <span className="px-1.5 py-0.5 md:px-2 md:py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 rounded-md text-[10px] md:text-xs font-medium font-inter shadow-[0_0_3px_rgba(0,0,0,0.03)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)]">
                    Actives
                  </span>
                  <span className="px-1.5 py-0.5 md:px-2 md:py-1 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-md text-[10px] md:text-xs font-inter">
                    Terminées
                  </span>
                </div>
              </div>

              <div className="space-y-2 md:space-y-3">
                <div className="flex items-center p-1.5 md:p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                  <CheckCircle2 className="h-4 w-4 md:h-5 md:w-5 text-green-500 mr-2 md:mr-3" />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs md:text-sm font-medium font-inter tracking-tight truncate">
                      Mise à jour du modèle de langage
                    </div>
                    <div className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 font-inter">
                      Échéance: Aujourd'hui
                    </div>
                  </div>
                  <div className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-[10px] md:text-xs text-blue-600 dark:text-blue-300 font-inter shadow-[0_0_3px_rgba(0,0,0,0.03)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)] flex-shrink-0 ml-1">
                    ML
                  </div>
                </div>

                <div className="flex items-center p-1.5 md:p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                  <CheckCircle2 className="h-4 w-4 md:h-5 md:w-5 text-green-500 mr-2 md:mr-3" />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs md:text-sm font-medium font-inter tracking-tight truncate">
                      Intégration CRM
                    </div>
                    <div className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 font-inter">
                      Échéance: Demain
                    </div>
                  </div>
                  <div className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center text-[10px] md:text-xs text-purple-600 dark:text-purple-300 font-inter shadow-[0_0_3px_rgba(0,0,0,0.03)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)] flex-shrink-0 ml-1">
                    JD
                  </div>
                </div>

                <div className="hidden sm:flex items-center p-1.5 md:p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-all duration-200">
                  <CheckCircle2 className="h-4 w-4 md:h-5 md:w-5 text-green-500 mr-2 md:mr-3" />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs md:text-sm font-medium font-inter tracking-tight truncate">
                      Tests de performance
                    </div>
                    <div className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 font-inter">
                      Échéance: 3 jours
                    </div>
                  </div>
                  <div className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-[10px] md:text-xs text-green-600 dark:text-green-300 font-inter shadow-[0_0_3px_rgba(0,0,0,0.03)] dark:shadow-[0_0_3px_rgba(0,0,0,0.1)] flex-shrink-0 ml-1">
                    SB
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1 md:gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-2 md:p-4 shadow-[0_0_8px_rgba(0,0,0,0.05)] dark:shadow-[0_0_8px_rgba(0,0,0,0.15)] flex flex-col items-center justify-center">
                <div className="text-lg md:text-3xl font-bold text-purple-600 dark:text-purple-400 font-inter">124</div>
                <div className="text-[10px] md:text-sm text-gray-500 dark:text-gray-400 font-inter">Conversations</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-2 md:p-4 shadow-[0_0_8px_rgba(0,0,0,0.05)] dark:shadow-[0_0_8px_rgba(0,0,0,0.15)] flex flex-col items-center justify-center">
                <div className="text-lg md:text-3xl font-bold text-blue-600 dark:text-blue-400 font-inter">32</div>
                <div className="text-[10px] md:text-sm text-gray-500 dark:text-gray-400 font-inter">En cours</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-2 md:p-4 shadow-[0_0_8px_rgba(0,0,0,0.05)] dark:shadow-[0_0_8px_rgba(0,0,0,0.15)] flex flex-col items-center justify-center">
                <div className="text-lg md:text-3xl font-bold text-green-600 dark:text-green-400 font-inter">98%</div>
                <div className="text-[10px] md:text-sm text-gray-500 dark:text-gray-400 font-inter">Satisfaction</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

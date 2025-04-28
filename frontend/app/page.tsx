import { Bot, Headphones, Zap, CheckCircle2, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import FeatureCard from "@/components/feature-card"
import TestimonialCard from "@/components/testimonial-card"
import ProductScreenshot from "@/components/product-screenshot"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-grow">
        {/* Hero Section - New Style */}
        <section className="relative py-8 md:py-20 overflow-hidden">
          {/* Background gradient circle */}
          <div className="absolute top-0 right-0 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-purple-100/80 to-blue-100/80 dark:from-purple-900/20 dark:to-blue-900/20 blur-3xl -z-10"></div>

          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6 max-w-4xl mx-auto leading-tight">
              <span className="block">Automatisez Votre</span>
              <span className="text-purple-600 dark:text-purple-400">Entreprise</span>
              <span className="block md:inline">
                <span className="hidden md:inline">,</span> Simplifiez Votre
              </span>
              <span className="text-blue-600 dark:text-blue-400"> Vie</span>
            </h1>

            <p className="text-sm md:text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-6 md:mb-10 px-2">
              Plateforme d'IA qui automatise vos tâches et améliore votre efficacité.
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-3 md:gap-4 mb-8 md:mb-16 px-4">
              <Button
                size="sm"
                className="bg-purple-600 hover:bg-purple-700 text-white rounded-full px-4 md:px-8 py-2 text-xs md:text-base"
              >
                Commencer maintenant
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-purple-200 text-purple-600 hover:bg-purple-50 dark:border-purple-800 dark:text-purple-400 dark:hover:bg-purple-900/20 rounded-full px-4 md:px-8 py-2 text-xs md:text-base mt-3 sm:mt-0"
              >
                Voir la démo
              </Button>
            </div>

            {/* Product Screenshot */}
            <div className="px-2 md:px-0">
              <ProductScreenshot />
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-gray-50 dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <div className="inline-block px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 rounded-full text-sm font-medium mb-4">
                Fonctionnalités
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Solutions d'automatisation IA</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Découvrez comment BerinIA peut transformer votre entreprise avec des solutions d'IA sur mesure.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <FeatureCard
                icon={<Bot className="h-10 w-10 text-purple-500" />}
                title="Chatbots Intelligents"
                description="Des chatbots qui comprennent réellement vos clients et résolvent leurs problèmes instantanément."
              />
              <FeatureCard
                icon={<Headphones className="h-10 w-10 text-blue-500" />}
                title="Standard Téléphonique IA"
                description="Automatisez votre standard téléphonique avec une IA qui comprend et dirige les appels avec précision."
              />
              <FeatureCard
                icon={<Zap className="h-10 w-10 text-indigo-500" />}
                title="Automatisation des Processus"
                description="Optimisez vos flux de travail grâce à l'automatisation intelligente des tâches répétitives."
              />
            </div>
          </div>
        </section>

        {/* Use Cases Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <div className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium mb-4">
                Cas d'usage
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Comment nos clients utilisent BerinIA</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Des solutions adaptées à chaque secteur d'activité et à chaque besoin.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 flex items-center justify-center mr-2">
                      1
                    </span>
                    Agences immobilières
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Automatisation des réponses aux demandes de visites et qualification des prospects avec un chatbot
                    disponible 24/7.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-purple-600 dark:text-purple-400">Résultat :</span>
                    <span className="ml-2">+40% de leads qualifiés, -60% de temps passé sur les demandes basiques</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 flex items-center justify-center mr-2">
                      2
                    </span>
                    Cabinets d'avocats
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Standard téléphonique IA qui trie les appels, qualifie l'urgence et programme les rendez-vous
                    automatiquement.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-blue-600 dark:text-blue-400">Résultat :</span>
                    <span className="ml-2">Économie de 25h/semaine pour les assistants juridiques</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-300 flex items-center justify-center mr-2">
                      3
                    </span>
                    E-commerce
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Chatbot de support client qui gère les questions sur les commandes, les retours et les échanges sans
                    intervention humaine.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-green-600 dark:text-green-400">Résultat :</span>
                    <span className="ml-2">Réduction de 70% des tickets de support, satisfaction client à 94%</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-300 flex items-center justify-center mr-2">
                      4
                    </span>
                    Cabinets comptables
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Automatisation de la collecte de documents et des relances clients avec suivi intelligent des
                    dossiers.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-orange-600 dark:text-orange-400">Résultat :</span>
                    <span className="ml-2">Réduction de 50% du temps de gestion administrative</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-pink-100 dark:bg-pink-900/30 text-pink-600 dark:text-pink-300 flex items-center justify-center mr-2">
                      5
                    </span>
                    Plombiers & Artisans
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Gestion des appels d'urgence et prise de rendez-vous automatisée, avec qualification des demandes et
                    estimation des délais d'intervention.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-pink-600 dark:text-pink-400">Résultat :</span>
                    <span className="ml-2">Réduction de 80% des appels manqués, +35% de clients satisfaits</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 flex items-center">
                    <span className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-300 flex items-center justify-center mr-2">
                      6
                    </span>
                    Salons de bien-être
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Système de réservation intelligent avec recommandations personnalisées de soins et suivi client
                    automatisé après les prestations.
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium text-teal-600 dark:text-teal-400">Résultat :</span>
                    <span className="ml-2">+45% de réservations additionnelles, fidélisation client améliorée</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Expanded Testimonials Section */}
        <section className="py-20 bg-gray-50 dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <div className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-300 rounded-full text-sm font-medium mb-4">
                Témoignages
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Ce que nos clients disent</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Découvrez comment BerinIA a transformé les entreprises de nos clients.
              </p>
              <div className="flex justify-center mt-6 space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star key={star} className="h-6 w-6 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="mt-2 text-lg font-medium">Note moyenne de 4.9/5 basée sur 120+ avis</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <TestimonialCard
                quote="BerinIA a révolutionné notre service client. Notre taux de satisfaction a augmenté de 40% en seulement 3 mois, et notre équipe de 5 personnes peut désormais gérer le double de demandes."
                author="Marie Dupont"
                company="Agence Digitale 360"
                avatarUrl="/placeholder.svg?height=100&width=100"
              />
              <TestimonialCard
                quote="Le standard téléphonique IA de BerinIA nous a permis d'économiser plus de 30 heures par semaine. Pour une petite structure comme la nôtre, c'est un gain de temps inestimable."
                author="Jean Martin"
                company="Cabinet Martin & Associés"
                avatarUrl="/placeholder.svg?height=100&width=100"
              />
              <TestimonialCard
                quote="L'implémentation a été rapide et les résultats immédiats. Un investissement qui s'est rentabilisé en moins de 2 mois pour notre cabinet de 12 collaborateurs."
                author="Sophie Leclerc"
                company="Expertise Comptable Plus"
                avatarUrl="/placeholder.svg?height=100&width=100"
              />
            </div>

            {/* Additional Proof Points */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <h3 className="text-xl font-bold mb-4">Résultats prouvés</h3>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>
                      Augmentation moyenne de <strong>42%</strong> du taux de conversion des leads
                    </span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>
                      Réduction de <strong>65%</strong> du temps de traitement des demandes clients
                    </span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>
                      Économie moyenne de <strong>25 000€</strong> par an sur les coûts opérationnels
                    </span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>
                      Disponibilité <strong>24/7</strong> avec une réponse instantanée aux clients
                    </span>
                  </li>
                </ul>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <h3 className="text-xl font-bold mb-4">Ils nous font confiance</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/agence-digitale-logo.png"
                      alt="Agence Digitale"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">Agence Digitale 360</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/cabinet-conseil-logo.png"
                      alt="Cabinet Conseil"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">Conseil & Stratégie</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/immobilier-logo.png"
                      alt="Immobilier"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">Immo Premium</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/cabinet-avocat-logo.png"
                      alt="Cabinet d'Avocats"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">Cabinet Martin & Associés</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/startup-tech-logo.png"
                      alt="Startup Tech"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">TechNova</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <img
                      src="/images/clients/cabinet-comptable-logo.png"
                      alt="Cabinet Comptable"
                      className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                    />
                    <span className="text-sm mt-2">Expertise Comptable Plus</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-500">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">Prêt à transformer votre entreprise ?</h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto mb-8">
              Rejoignez les centaines d'entreprises qui ont déjà adopté BerinIA pour automatiser leurs processus.
            </p>
            <div className="flex justify-center">
              <Button size="lg" variant="secondary" className="hover:scale-105 transition-transform duration-300">
                Démarrer maintenant
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

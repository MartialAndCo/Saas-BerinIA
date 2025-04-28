import { ArrowRight, CheckCircle2, Handshake, Building, Globe, Award } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function PartnersPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-grow">
        {/* Hero Section */}
        <section className="relative py-20 md:py-28 overflow-hidden">
          <AnimatedGradient />

          <div className="container mx-auto px-4 relative z-10">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                Nos{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  Partenaires
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Découvrez l'écosystème de partenaires qui nous permet de vous offrir des solutions d'IA de pointe.
              </p>
            </div>
          </div>
        </section>

        {/* Partenaires Technologiques */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <div className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium mb-4">
                Partenaires Technologiques
              </div>
              <h2 className="text-3xl font-bold mb-6">Les meilleurs outils pour les meilleures solutions</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Nous collaborons avec les leaders de l'industrie pour vous offrir des solutions d'IA robustes et
                évolutives.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center max-w-5xl mx-auto">
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/openai-logo.png" alt="OpenAI" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">OpenAI</span>
              </div>
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/slack-logo.png" alt="Slack" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">Slack</span>
              </div>
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/n8n-logo.png" alt="n8n" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">n8n</span>
              </div>
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/langgraph-logo.png" alt="LangGraph" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">LangGraph</span>
              </div>
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/cursor-logo.png" alt="Cursor" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">Cursor</span>
              </div>
              <div className="flex flex-col items-center transform hover:scale-110 transition-transform duration-300">
                <img src="/images/partners/v0-logo.png" alt="V0.dev" className="h-16 mb-3 object-contain" />
                <span className="text-sm font-medium">V0.dev</span>
              </div>
            </div>

            <div className="mt-16 bg-gray-50 dark:bg-gray-800 rounded-xl p-8 max-w-5xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-2xl font-bold mb-4">Pourquoi nous choisissons les meilleurs partenaires</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    Chez BerinIA, nous intégrons les technologies les plus avancées pour créer des solutions d'IA
                    robustes et évolutives. Notre écosystème de partenaires nous permet de vous offrir :
                  </p>
                  <ul className="space-y-3">
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Des modèles d'IA de pointe avec OpenAI</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Des workflows d'automatisation puissants avec n8n</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Des agents IA avancés grâce à LangGraph</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Une intégration transparente avec vos outils existants comme Slack</span>
                    </li>
                  </ul>
                </div>
                <div className="bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-xl p-8">
                  <blockquote className="text-lg italic">
                    "Notre partenariat avec ces leaders technologiques nous permet d'innover constamment et d'offrir des
                    solutions d'IA qui sont toujours à la pointe de ce qui est possible."
                  </blockquote>
                  <div className="mt-4 flex items-center">
                    <div className="w-12 h-12 rounded-full bg-purple-200 flex items-center justify-center mr-3">
                      <span className="font-medium">PD</span>
                    </div>
                    <div>
                      <p className="font-medium">Pierre Durand</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">CTO, BerinIA</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Clients Partenaires */}
        <section className="py-16 bg-gray-50 dark:bg-gray-800">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <div className="inline-block px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 rounded-full text-sm font-medium mb-4">
                Clients Partenaires
              </div>
              <h2 className="text-3xl font-bold mb-6">Ils nous font confiance</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Des entreprises de toutes tailles et de tous secteurs utilisent BerinIA pour transformer leur relation
                client.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 max-w-5xl mx-auto">
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/carrefour-logo.png"
                  alt="Carrefour"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/bnp-logo.png"
                  alt="BNP Paribas"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/orange-logo.png"
                  alt="Orange"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/decathlon-logo.png"
                  alt="Decathlon"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/bouygues-logo.png"
                  alt="Bouygues"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col items-center">
                <img
                  src="/images/clients/societe-generale-logo.png"
                  alt="Société Générale"
                  className="h-12 object-contain hover:scale-110 transition-transform duration-300"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-16">
              <Card className="bg-white dark:bg-gray-900">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-3">
                      <Building className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold">Grands Comptes</h3>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Nous accompagnons les grandes entreprises dans leur transformation digitale avec des solutions d'IA
                    sur mesure.
                  </p>
                  <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Intégration avec vos systèmes existants</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Solutions hautement personnalisées</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Support dédié 24/7</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-white dark:bg-gray-900">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3">
                      <Building className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold">PME</h3>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Nous aidons les PME à rester compétitives grâce à des solutions d'IA accessibles et efficaces.
                  </p>
                  <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Solutions clés en main</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Tarifs adaptés</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Mise en place rapide</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-white dark:bg-gray-900">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mr-3">
                      <Globe className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <h3 className="text-xl font-bold">Startups</h3>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Nous soutenons les startups innovantes avec notre programme d'accompagnement spécial.
                  </p>
                  <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Tarifs préférentiels</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Accompagnement technique</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Accès à notre réseau</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Programme de Partenariat */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <div className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-300 rounded-full text-sm font-medium mb-4">
                Programme de Partenariat
              </div>
              <h2 className="text-3xl font-bold mb-6">Devenez partenaire BerinIA</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Rejoignez notre réseau de partenaires et développez votre activité en proposant nos solutions d'IA à vos
                clients.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-5xl mx-auto">
              <div>
                <h3 className="text-2xl font-bold mb-6 flex items-center">
                  <Handshake className="h-6 w-6 text-purple-600 dark:text-purple-400 mr-2" />
                  Avantages du programme
                </h3>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">Commissions attractives</span>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        Bénéficiez de commissions allant jusqu'à 30% sur les ventes que vous générez.
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">Formation et certification</span>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        Accédez à notre programme de formation et obtenez la certification BerinIA Partner.
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">Support marketing</span>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        Recevez des ressources marketing et des supports de vente pour promouvoir nos solutions.
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">Support technique dédié</span>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        Bénéficiez d'un accès prioritaire à notre équipe technique pour vous accompagner.
                      </p>
                    </div>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-2xl font-bold mb-6 flex items-center">
                  <Award className="h-6 w-6 text-blue-600 dark:text-blue-400 mr-2" />
                  Types de partenariats
                </h3>
                <div className="space-y-6">
                  <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl">
                    <h4 className="text-lg font-bold mb-2">Partenaire Revendeur</h4>
                    <p className="text-gray-600 dark:text-gray-300 mb-3">
                      Revendez nos solutions à vos clients et bénéficiez de commissions attractives.
                    </p>
                    <Button variant="outline" size="sm" className="group">
                      En savoir plus
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl">
                    <h4 className="text-lg font-bold mb-2">Partenaire Technologique</h4>
                    <p className="text-gray-600 dark:text-gray-300 mb-3">
                      Intégrez nos API et SDK dans vos propres solutions pour les enrichir avec nos capacités d'IA.
                    </p>
                    <Button variant="outline" size="sm" className="group">
                      En savoir plus
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl">
                    <h4 className="text-lg font-bold mb-2">Partenaire Consultant</h4>
                    <p className="text-gray-600 dark:text-gray-300 mb-3">
                      Accompagnez vos clients dans l'implémentation et l'optimisation de nos solutions.
                    </p>
                    <Button variant="outline" size="sm" className="group">
                      En savoir plus
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-500">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">
              Rejoignez notre écosystème de partenaires
            </h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto mb-8">
              Ensemble, créons des solutions d'IA qui transforment les entreprises et améliorent l'expérience client.
            </p>
            <Button size="lg" variant="secondary" className="hover:scale-105 transition-transform duration-300">
              Devenir partenaire
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

import { ArrowRight, CheckCircle2, Users, Award, Lightbulb, Target, Heart } from "lucide-react"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function AboutPage() {
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
                À propos de{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  BerinIA
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Nous transformons la façon dont les entreprises interagissent avec leurs clients grâce à l'intelligence
                artificielle.
              </p>
            </div>
          </div>
        </section>

        {/* Notre Histoire */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold mb-6">Notre Histoire</h2>
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <p>
                  BerinIA a été fondée en 2020 par une équipe d'experts en intelligence artificielle et en expérience
                  client, unis par une vision commune : rendre l'IA accessible et utile pour toutes les entreprises,
                  quelle que soit leur taille.
                </p>
                <p>
                  Face à un marché où les solutions d'IA étaient soit trop complexes, soit trop coûteuses pour les PME,
                  nous avons décidé de créer une plateforme qui démocratise l'accès à cette technologie transformative.
                </p>
                <p>
                  Après deux ans de développement intensif et de collaboration étroite avec nos premiers clients, nous
                  avons lancé notre plateforme en 2022. Depuis, nous avons aidé plus de 500 entreprises à transformer
                  leur relation client et à optimiser leurs processus grâce à l'IA.
                </p>
                <p>
                  Aujourd'hui, BerinIA est reconnue comme un leader dans le domaine de l'automatisation intelligente
                  pour les PME, avec une présence dans toute la France et une expansion européenne en cours.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Notre Mission */}
        <section className="py-16 bg-gray-50 dark:bg-gray-800">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-6">Notre Mission</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Démocratiser l'intelligence artificielle pour permettre à toutes les entreprises de prospérer à l'ère
                numérique.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left mt-12">
                <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-3">
                      <Target className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold">Notre Vision</h3>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300">
                    Un monde où chaque entreprise, quelle que soit sa taille, peut tirer parti de l'IA pour offrir des
                    expériences exceptionnelles à ses clients et optimiser ses opérations.
                  </p>
                </div>

                <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3">
                      <Heart className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold">Nos Valeurs</h3>
                  </div>
                  <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Innovation responsable</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Accessibilité et inclusivité</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Excellence et amélioration continue</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <span>Transparence et confiance</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Notre Équipe */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <h2 className="text-3xl font-bold mb-6">Notre Équipe</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Une équipe passionnée d'experts en IA, en développement et en expérience client.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
              {/* Fondateur & CEO */}
              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="h-48 bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center">
                  <Users className="h-24 w-24 text-white" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-1">Sophie Martin</h3>
                  <p className="text-sm text-purple-600 dark:text-purple-400 mb-3">Fondatrice & CEO</p>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Ancienne directrice de l'innovation chez un leader de l'IA, Sophie a fondé BerinIA avec la vision de
                    démocratiser l'accès à l'IA pour toutes les entreprises.
                  </p>
                </div>
              </div>

              {/* CTO */}
              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="h-48 bg-gradient-to-r from-blue-400 to-indigo-400 flex items-center justify-center">
                  <Users className="h-24 w-24 text-white" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-1">Pierre Durand</h3>
                  <p className="text-sm text-blue-600 dark:text-blue-400 mb-3">CTO</p>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Expert en IA et en développement de systèmes complexes, Pierre dirige notre équipe technique et
                    supervise l'architecture de notre plateforme.
                  </p>
                </div>
              </div>

              {/* COO */}
              <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                <div className="h-48 bg-gradient-to-r from-indigo-400 to-purple-400 flex items-center justify-center">
                  <Users className="h-24 w-24 text-white" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-1">Thomas Bernard</h3>
                  <p className="text-sm text-indigo-600 dark:text-indigo-400 mb-3">COO</p>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Fort de 15 ans d'expérience dans le conseil aux entreprises, Thomas veille à ce que nos solutions
                    répondent parfaitement aux besoins de nos clients.
                  </p>
                </div>
              </div>
            </div>

            <div className="text-center mt-12">
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Notre équipe compte aujourd'hui plus de 30 collaborateurs passionnés, répartis entre nos bureaux de
                Paris, Lyon et Bordeaux.
              </p>
              <Button variant="outline" className="group">
                Rejoignez notre équipe
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </div>
          </div>
        </section>

        {/* Nos Engagements */}
        <section className="py-16 bg-gray-50 dark:bg-gray-800">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <h2 className="text-3xl font-bold mb-6">Nos Engagements</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Chez BerinIA, nous croyons que la technologie doit être une force positive pour la société.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mr-3">
                    <Lightbulb className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-xl font-bold">IA Responsable</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  Nous développons nos solutions d'IA selon des principes éthiques stricts, en veillant à ce qu'elles
                  soient équitables, transparentes et respectueuses de la vie privée.
                </p>
                <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Transparence algorithmique</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Lutte contre les biais</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Protection des données</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center mr-3">
                    <Award className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <h3 className="text-xl font-bold">Impact Social</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  Nous nous engageons à avoir un impact positif sur la société, en rendant l'IA accessible aux petites
                  entreprises et en soutenant des initiatives sociales.
                </p>
                <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Programme d'accompagnement pour les startups</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Soutien aux associations via notre programme 1%</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span>Formation et sensibilisation à l'IA</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-500">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">Rejoignez l'aventure BerinIA</h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto mb-8">
              Découvrez comment nous pouvons transformer votre entreprise grâce à l'IA ou rejoignez notre équipe pour
              construire le futur.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" className="hover:scale-105 transition-transform duration-300">
                Demander une démo
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="bg-transparent text-white border-white hover:bg-white/10 hover:scale-105 transition-all duration-300"
              >
                Carrières
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

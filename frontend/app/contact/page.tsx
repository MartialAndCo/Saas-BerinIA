import { Mail, Phone, MapPin, Clock, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function ContactPage() {
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
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  Contactez-nous
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Notre équipe est à votre disposition pour répondre à toutes vos questions et vous accompagner dans votre
                projet.
              </p>
            </div>
          </div>
        </section>

        {/* Contact Form Section */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
              {/* Contact Form */}
              <div>
                <h2 className="text-2xl font-bold mb-6">Envoyez-nous un message</h2>
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="name">Nom complet</Label>
                      <Input id="name" placeholder="Jean Dupont" required />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email professionnel</Label>
                      <Input id="email" type="email" placeholder="jean@entreprise.com" required />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Téléphone</Label>
                      <Input id="phone" placeholder="06 12 34 56 78" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="company">Entreprise</Label>
                      <Input id="company" placeholder="Nom de votre entreprise" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Je souhaite</Label>
                    <RadioGroup defaultValue="demo">
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="demo" id="demo" />
                        <Label htmlFor="demo">Demander une démo</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="info" id="info" />
                        <Label htmlFor="info">Obtenir plus d'informations</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="partner" id="partner" />
                        <Label htmlFor="partner">Devenir partenaire</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="other" id="other" />
                        <Label htmlFor="other">Autre demande</Label>
                      </div>
                    </RadioGroup>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">Message</Label>
                    <Textarea id="message" placeholder="Comment pouvons-nous vous aider ?" rows={5} required />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
                  >
                    Envoyer le message
                  </Button>
                </form>
              </div>

              {/* Contact Info */}
              <div>
                <h2 className="text-2xl font-bold mb-6">Nos coordonnées</h2>

                <div className="space-y-8">
                  <div className="flex items-start">
                    <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-4">
                      <Mail className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-1">Email</h3>
                      <p className="text-gray-600 dark:text-gray-300">contact@berinia.com</p>
                      <p className="text-gray-600 dark:text-gray-300">support@berinia.com (support technique)</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-4">
                      <Phone className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-1">Téléphone</h3>
                      <p className="text-gray-600 dark:text-gray-300">+33 (0)1 23 45 67 89</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Du lundi au vendredi, 9h-18h</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mr-4">
                      <MapPin className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-1">Adresse</h3>
                      <p className="text-gray-600 dark:text-gray-300">
                        123 Avenue de l'Innovation
                        <br />
                        75008 Paris, France
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mr-4">
                      <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-1">Horaires d'ouverture</h3>
                      <p className="text-gray-600 dark:text-gray-300">
                        Lundi - Vendredi: 9h00 - 18h00
                        <br />
                        Samedi - Dimanche: Fermé
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-10 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-bold mb-4">Nos bureaux</h3>
                  <div className="space-y-4">
                    <div className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-medium">Paris (Siège social)</span>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          123 Avenue de l'Innovation, 75008 Paris
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-medium">Lyon</span>
                        <p className="text-sm text-gray-600 dark:text-gray-300">45 Rue de la République, 69002 Lyon</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-medium">Bordeaux</span>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          78 Cours de l'Intendance, 33000 Bordeaux
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-16 bg-gray-50 dark:bg-gray-800">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-12">
              <div className="inline-block px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-300 rounded-full text-sm font-medium mb-4">
                Questions fréquentes
              </div>
              <h2 className="text-3xl font-bold mb-6">Besoin d'aide ?</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Consultez nos réponses aux questions les plus fréquemment posées.
              </p>
            </div>

            <div className="max-w-3xl mx-auto">
              <Accordion type="single" collapsible className="space-y-4">
                <AccordionItem
                  value="item-1"
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    Comment puis-je obtenir une démo de vos solutions ?
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      Vous pouvez demander une démo en remplissant le formulaire de contact sur cette page ou en nous
                      appelant directement au +33 (0)1 23 45 67 89. Un de nos experts vous contactera dans les 24 heures
                      pour organiser une démonstration personnalisée adaptée à vos besoins.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem
                  value="item-2"
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    Quel est le délai de réponse à une demande de contact ?
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      Nous nous engageons à répondre à toutes les demandes de contact dans un délai de 24 heures
                      ouvrées. Pour les demandes urgentes, nous vous recommandons de nous appeler directement.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem
                  value="item-3"
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    Comment fonctionne le support technique ?
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      Notre support technique est disponible par email à support@berinia.com et par téléphone au +33
                      (0)1 23 45 67 89, du lundi au vendredi de 9h à 18h. Les clients ayant souscrit à nos forfaits
                      Business et Enterprise bénéficient également d'un support prioritaire et d'un gestionnaire de
                      compte dédié.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem
                  value="item-4"
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    Comment devenir partenaire BerinIA ?
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      Pour devenir partenaire, sélectionnez l'option "Devenir partenaire" dans notre formulaire de
                      contact ou visitez notre page Partenaires. Notre équipe partenaires vous contactera pour discuter
                      des différentes options de partenariat et vous accompagner dans le processus.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem
                  value="item-5"
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    Proposez-vous des formations pour utiliser vos solutions ?
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      Oui, nous proposons des formations pour tous nos clients afin de les aider à tirer le meilleur
                      parti de nos solutions. Ces formations peuvent être réalisées en présentiel dans nos locaux ou à
                      distance selon vos préférences. Contactez-nous pour en savoir plus sur notre programme de
                      formation.
                    </p>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>
        </section>

        {/* Map Section */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">Nous trouver</h2>
              <div className="aspect-video bg-gray-200 dark:bg-gray-700 rounded-xl overflow-hidden">
                {/* Placeholder for a map - In a real implementation, you would use Google Maps or another map provider */}
                <div className="w-full h-full flex items-center justify-center">
                  <p className="text-gray-500 dark:text-gray-400">Carte interactive de nos bureaux</p>
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
              Contactez-nous dès aujourd'hui pour découvrir comment BerinIA peut vous aider à automatiser vos processus
              et améliorer votre relation client.
            </p>
            <Button size="lg" variant="secondary" className="hover:scale-105 transition-transform duration-300">
              Demander une démo
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

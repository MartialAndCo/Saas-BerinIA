import ScrollToTopLink from "./scroll-to-top-link"
import { Facebook, Twitter, Instagram, Linkedin, Github } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <ScrollToTopLink href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-blue-500"></div>
              <span className="text-xl font-bold">BerinIA</span>
            </ScrollToTopLink>
            <p className="text-gray-600 dark:text-gray-400">
              Transformez votre entreprise avec des solutions d'IA avancées.
            </p>
            <div className="flex space-x-4">
              <ScrollToTopLink
                href="#"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
              >
                <Facebook className="h-5 w-5" />
                <span className="sr-only">Facebook</span>
              </ScrollToTopLink>
              <ScrollToTopLink
                href="#"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
              >
                <Twitter className="h-5 w-5" />
                <span className="sr-only">Twitter</span>
              </ScrollToTopLink>
              <ScrollToTopLink
                href="#"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
              >
                <Instagram className="h-5 w-5" />
                <span className="sr-only">Instagram</span>
              </ScrollToTopLink>
              <ScrollToTopLink
                href="#"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
              >
                <Linkedin className="h-5 w-5" />
                <span className="sr-only">LinkedIn</span>
              </ScrollToTopLink>
              <ScrollToTopLink
                href="#"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
              >
                <Github className="h-5 w-5" />
                <span className="sr-only">GitHub</span>
              </ScrollToTopLink>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-900 dark:text-gray-100 mb-4">
              Produits
            </h3>
            <ul className="space-y-3">
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Chatbots IA
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Standard Téléphonique
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Automatisation
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Analyse de Données
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Intégrations
                </ScrollToTopLink>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-900 dark:text-gray-100 mb-4">
              Ressources
            </h3>
            <ul className="space-y-3">
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Documentation
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Guides
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Blog
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Études de cas
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Webinaires
                </ScrollToTopLink>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-900 dark:text-gray-100 mb-4">
              Entreprise
            </h3>
            <ul className="space-y-3">
              <li>
                <ScrollToTopLink
                  href="/a-propos"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  À propos
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Carrières
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="/partenaires"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Partenaires
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="/contact"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Contact
                </ScrollToTopLink>
              </li>
              <li>
                <ScrollToTopLink
                  href="#"
                  className="text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
                >
                  Presse
                </ScrollToTopLink>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              &copy; {new Date().getFullYear()} BerinIA. Tous droits réservés.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <ScrollToTopLink
                href="/conditions-utilisation"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors text-sm"
              >
                Conditions d'utilisation
              </ScrollToTopLink>
              <ScrollToTopLink
                href="/confidentialite"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors text-sm"
              >
                Politique de confidentialité
              </ScrollToTopLink>
              <ScrollToTopLink
                href="/cookies"
                className="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors text-sm"
              >
                Cookies
              </ScrollToTopLink>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

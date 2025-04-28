import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function CookiesPage() {
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
                Politique des{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  cookies
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">Dernière mise à jour : 15 avril 2023</p>
            </div>
          </div>
        </section>

        {/* Cookies Content */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <h2>1. Introduction</h2>
                <p>
                  Cette politique en matière de cookies explique ce que sont les cookies, comment BerinIA ("nous",
                  "notre", "nos") utilise les cookies et technologies similaires sur notre site web et nos applications,
                  et quelles options vous avez concernant ces cookies.
                </p>
                <p>
                  En continuant à utiliser notre site web et nos applications, vous consentez à l'utilisation de cookies
                  comme décrit dans cette politique.
                </p>

                <h2>2. Qu'est-ce qu'un cookie ?</h2>
                <p>
                  Un cookie est un petit fichier texte qui est stocké sur votre ordinateur ou appareil mobile lorsque
                  vous visitez un site web. Les cookies sont largement utilisés pour faire fonctionner les sites web ou
                  les faire fonctionner plus efficacement, ainsi que pour fournir des informations aux propriétaires du
                  site.
                </p>
                <p>
                  Les cookies peuvent être des "cookies persistants" ou des "cookies de session". Les cookies
                  persistants restent sur votre ordinateur ou appareil mobile lorsque vous vous déconnectez, tandis que
                  les cookies de session sont supprimés dès que vous fermez votre navigateur web.
                </p>

                <h2>3. Comment nous utilisons les cookies</h2>
                <p>Nous utilisons différents types de cookies pour diverses raisons :</p>

                <h3>3.1 Cookies essentiels</h3>
                <p>
                  Ces cookies sont nécessaires au fonctionnement de notre site web et ne peuvent pas être désactivés
                  dans nos systèmes. Ils sont généralement établis en réponse à des actions que vous effectuez et qui
                  constituent une demande de services, telles que la définition de vos préférences de confidentialité,
                  la connexion ou le remplissage de formulaires. Vous pouvez configurer votre navigateur pour qu'il
                  bloque ou vous alerte de l'existence de ces cookies, mais certaines parties du site ne fonctionneront
                  pas. Ces cookies ne stockent aucune information personnellement identifiable.
                </p>

                <h3>3.2 Cookies de performance</h3>
                <p>
                  Ces cookies nous permettent de compter les visites et les sources de trafic afin que nous puissions
                  mesurer et améliorer les performances de notre site. Ils nous aident à savoir quelles pages sont les
                  plus et les moins populaires et à voir comment les visiteurs se déplacent sur le site. Toutes les
                  informations collectées par ces cookies sont agrégées et donc anonymes. Si vous n'autorisez pas ces
                  cookies, nous ne saurons pas quand vous avez visité notre site.
                </p>

                <h3>3.3 Cookies de fonctionnalité</h3>
                <p>
                  Ces cookies permettent au site de fournir une fonctionnalité et une personnalisation améliorées. Ils
                  peuvent être définis par nous ou par des fournisseurs tiers dont nous avons ajouté les services à nos
                  pages. Si vous n'autorisez pas ces cookies, certains ou tous ces services peuvent ne pas fonctionner
                  correctement.
                </p>

                <h3>3.4 Cookies de ciblage</h3>
                <p>
                  Ces cookies peuvent être définis par nos partenaires publicitaires via notre site. Ils peuvent être
                  utilisés par ces entreprises pour établir un profil de vos intérêts et vous montrer des publicités
                  pertinentes sur d'autres sites. Ils ne stockent pas directement des informations personnelles, mais
                  sont basés sur l'identification unique de votre navigateur et de votre appareil Internet. Si vous
                  n'autorisez pas ces cookies, vous connaîtrez une publicité moins ciblée.
                </p>

                <h2>4. Cookies tiers</h2>
                <p>
                  En plus de nos propres cookies, nous pouvons également utiliser divers cookies tiers pour signaler les
                  statistiques d'utilisation du site, diffuser des publicités et ainsi de suite. Ces cookies peuvent
                  inclure :
                </p>
                <ul>
                  <li>Google Analytics : pour analyser comment les utilisateurs utilisent notre site</li>
                  <li>Google Ads : pour mesurer l'efficacité de nos campagnes publicitaires</li>
                  <li>Facebook Pixel : pour mesurer l'efficacité de nos publicités sur Facebook</li>
                  <li>Hotjar : pour comprendre comment les utilisateurs interagissent avec notre site</li>
                </ul>

                <h2>5. Comment gérer les cookies</h2>
                <p>
                  La plupart des navigateurs web vous permettent de contrôler les cookies via les paramètres de votre
                  navigateur. Cependant, si vous limitez la capacité des sites web à définir des cookies, vous pouvez
                  dégrader votre expérience utilisateur globale, car elle ne sera plus personnalisée pour vous. Cela
                  pourrait également vous empêcher d'enregistrer des paramètres personnalisés, comme les informations de
                  connexion.
                </p>
                <p>Voici comment vous pouvez gérer les cookies dans les navigateurs les plus populaires :</p>
                <ul>
                  <li>
                    <strong>Chrome</strong> : Menu {">"} Paramètres {">"} Afficher les paramètres avancés {">"}{" "}
                    Confidentialité {">"} Paramètres de contenu {">"} Cookies
                  </li>
                  <li>
                    <strong>Firefox</strong> : Menu {">"} Options {">"} Vie privée {">"} Historique {">"} Paramètres
                    personnalisés pour l'historique {">"} Cookies
                  </li>
                  <li>
                    <strong>Safari</strong> : Préférences {">"} Confidentialité {">"} Cookies et données de site web
                  </li>
                  <li>
                    <strong>Edge</strong> : Menu {">"} Paramètres {">"} Afficher les paramètres avancés {">"}{" "}
                    Confidentialité et services {">"} Cookies
                  </li>
                </ul>

                <h2>6. Cookies spécifiques utilisés sur notre site</h2>
                <p>Voici une liste des cookies spécifiques que nous utilisons sur notre site :</p>
                <table>
                  <thead>
                    <tr>
                      <th>Nom du cookie</th>
                      <th>Type</th>
                      <th>Finalité</th>
                      <th>Durée</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>session_id</td>
                      <td>Essentiel</td>
                      <td>Utilisé pour maintenir votre session</td>
                      <td>Session</td>
                    </tr>
                    <tr>
                      <td>auth_token</td>
                      <td>Essentiel</td>
                      <td>Utilisé pour l'authentification</td>
                      <td>30 jours</td>
                    </tr>
                    <tr>
                      <td>preferences</td>
                      <td>Fonctionnalité</td>
                      <td>Stocke vos préférences utilisateur</td>
                      <td>1 an</td>
                    </tr>
                    <tr>
                      <td>_ga</td>
                      <td>Performance</td>
                      <td>Google Analytics - Utilisé pour distinguer les utilisateurs</td>
                      <td>2 ans</td>
                    </tr>
                    <tr>
                      <td>_gid</td>
                      <td>Performance</td>
                      <td>Google Analytics - Utilisé pour distinguer les utilisateurs</td>
                      <td>24 heures</td>
                    </tr>
                    <tr>
                      <td>_fbp</td>
                      <td>Ciblage</td>
                      <td>Facebook Pixel - Utilisé pour le ciblage publicitaire</td>
                      <td>3 mois</td>
                    </tr>
                  </tbody>
                </table>

                <h2>7. Modifications de notre politique en matière de cookies</h2>
                <p>
                  Nous pouvons mettre à jour cette politique en matière de cookies de temps à autre pour refléter, par
                  exemple, les changements apportés aux cookies que nous utilisons ou pour d'autres raisons
                  opérationnelles, légales ou réglementaires. Veuillez donc consulter régulièrement cette politique pour
                  rester informé de notre utilisation des cookies et des technologies connexes.
                </p>
                <p>La date en haut de cette politique indique quand elle a été mise à jour pour la dernière fois.</p>

                <h2>8. Contact</h2>
                <p>
                  Si vous avez des questions concernant notre utilisation des cookies ou d'autres technologies, veuillez
                  nous contacter à l'adresse suivante :
                </p>
                <p>
                  BerinIA
                  <br />
                  123 Avenue de l'Innovation
                  <br />
                  75008 Paris, France
                  <br />
                  Email : privacy@berinia.com
                </p>
              </div>

              <div className="mt-12 text-center">
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  Pour toute question concernant notre politique en matière de cookies, n'hésitez pas à nous contacter.
                </p>
                <Button variant="outline" className="group" asChild>
                  <Link href="/contact">
                    Nous contacter
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

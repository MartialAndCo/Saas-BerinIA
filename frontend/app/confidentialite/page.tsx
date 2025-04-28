import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function PrivacyPage() {
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
                Politique de{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  confidentialité
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">Dernière mise à jour : 15 avril 2023</p>
            </div>
          </div>
        </section>

        {/* Privacy Content */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <h2>1. Introduction</h2>
                <p>
                  Chez BerinIA, nous accordons une grande importance à la protection de vos données personnelles. Cette
                  politique de confidentialité explique comment nous collectons, utilisons, partageons et protégeons vos
                  informations lorsque vous utilisez notre site web, nos applications et nos services (collectivement,
                  les "Services").
                </p>
                <p>
                  En utilisant nos Services, vous acceptez les pratiques décrites dans cette politique de
                  confidentialité. Si vous n'acceptez pas cette politique, veuillez ne pas utiliser nos Services.
                </p>

                <h2>2. Informations que nous collectons</h2>
                <h3>2.1 Informations que vous nous fournissez</h3>
                <p>
                  Nous collectons les informations que vous nous fournissez directement lorsque vous utilisez nos
                  Services, notamment :
                </p>
                <ul>
                  <li>
                    Informations de compte : lorsque vous créez un compte, nous collectons votre nom, adresse e-mail,
                    mot de passe, et éventuellement votre numéro de téléphone et le nom de votre entreprise.
                  </li>
                  <li>
                    Informations de profil : vous pouvez également choisir de nous fournir des informations
                    supplémentaires pour votre profil, comme une photo, un titre de poste, etc.
                  </li>
                  <li>
                    Communications : lorsque vous nous contactez, nous collectons les informations que vous nous
                    fournissez dans ces communications.
                  </li>
                  <li>
                    Informations de paiement : si vous effectuez un achat, nous collectons les informations nécessaires
                    pour traiter votre paiement, bien que les détails complets de votre carte de crédit ne soient pas
                    stockés sur nos serveurs.
                  </li>
                </ul>

                <h3>2.2 Informations collectées automatiquement</h3>
                <p>
                  Lorsque vous utilisez nos Services, nous collectons automatiquement certaines informations, notamment
                  :
                </p>
                <ul>
                  <li>
                    Informations d'utilisation : nous enregistrons comment vous interagissez avec nos Services, comme
                    les pages que vous visitez, les fonctionnalités que vous utilisez, etc.
                  </li>
                  <li>
                    Informations sur l'appareil : nous collectons des informations sur l'appareil que vous utilisez pour
                    accéder à nos Services, comme le type d'appareil, le système d'exploitation, le navigateur, etc.
                  </li>
                  <li>
                    Informations de localisation : nous pouvons collecter des informations sur votre localisation
                    approximative à partir de votre adresse IP.
                  </li>
                  <li>
                    Cookies et technologies similaires : nous utilisons des cookies et d'autres technologies de suivi
                    pour collecter des informations sur votre utilisation de nos Services. Pour plus d'informations,
                    veuillez consulter notre politique en matière de cookies.
                  </li>
                </ul>

                <h2>3. Comment nous utilisons vos informations</h2>
                <p>Nous utilisons les informations que nous collectons pour :</p>
                <ul>
                  <li>Fournir, maintenir et améliorer nos Services</li>
                  <li>Créer et gérer votre compte</li>
                  <li>Traiter vos paiements</li>
                  <li>
                    Communiquer avec vous au sujet de nos Services, y compris pour vous envoyer des mises à jour, des
                    alertes de sécurité et des messages administratifs
                  </li>
                  <li>Répondre à vos commentaires, questions et demandes</li>
                  <li>Surveiller et analyser les tendances, l'utilisation et les activités liées à nos Services</li>
                  <li>Détecter, prévenir et résoudre les problèmes techniques et de sécurité</li>
                  <li>Personnaliser et améliorer votre expérience</li>
                  <li>Se conformer aux obligations légales</li>
                </ul>

                <h2>4. Comment nous partageons vos informations</h2>
                <p>
                  Nous ne vendons pas vos informations personnelles. Cependant, nous pouvons partager vos informations
                  dans les situations suivantes :
                </p>
                <ul>
                  <li>
                    Avec des fournisseurs de services : nous partageons vos informations avec des fournisseurs de
                    services tiers qui effectuent des services en notre nom, comme l'hébergement, l'analyse de données,
                    le traitement des paiements, etc.
                  </li>
                  <li>
                    Pour des raisons légales : nous pouvons partager vos informations si nous croyons de bonne foi que
                    cela est nécessaire pour se conformer à la loi, protéger nos droits ou prévenir la fraude ou
                    d'autres activités illégales.
                  </li>
                  <li>
                    Avec votre consentement : nous pouvons partager vos informations avec des tiers lorsque vous nous
                    donnez votre consentement pour le faire.
                  </li>
                  <li>
                    Dans le cadre d'une transaction commerciale : si nous sommes impliqués dans une fusion, acquisition
                    ou vente d'actifs, vos informations peuvent être transférées dans le cadre de cette transaction.
                  </li>
                </ul>

                <h2>5. Sécurité des données</h2>
                <p>
                  Nous prenons des mesures raisonnables pour protéger vos informations contre la perte, le vol,
                  l'utilisation abusive et l'accès non autorisé, la divulgation, l'altération et la destruction.
                  Cependant, aucune méthode de transmission sur Internet ou de stockage électronique n'est totalement
                  sécurisée, et nous ne pouvons garantir la sécurité absolue de vos informations.
                </p>

                <h2>6. Conservation des données</h2>
                <p>
                  Nous conservons vos informations aussi longtemps que nécessaire pour fournir nos Services et pour les
                  autres fins essentielles telles que le respect de nos obligations légales, la résolution des litiges
                  et l'application de nos politiques.
                </p>

                <h2>7. Vos droits</h2>
                <p>
                  Selon votre lieu de résidence, vous pouvez avoir certains droits concernant vos informations
                  personnelles, notamment :
                </p>
                <ul>
                  <li>Le droit d'accéder à vos informations personnelles</li>
                  <li>Le droit de rectifier ou mettre à jour vos informations personnelles</li>
                  <li>Le droit de supprimer vos informations personnelles</li>
                  <li>Le droit de restreindre ou de vous opposer au traitement de vos informations personnelles</li>
                  <li>Le droit à la portabilité des données</li>
                  <li>Le droit de retirer votre consentement</li>
                </ul>
                <p>
                  Pour exercer ces droits, veuillez nous contacter en utilisant les coordonnées fournies à la fin de
                  cette politique.
                </p>

                <h2>8. Transferts internationaux de données</h2>
                <p>
                  Nous pouvons transférer, stocker et traiter vos informations dans des pays autres que votre pays de
                  résidence. Ces pays peuvent avoir des lois sur la protection des données différentes de celles de
                  votre pays. Nous prenons des mesures pour nous assurer que vos informations bénéficient d'un niveau de
                  protection adéquat lorsqu'elles sont transférées internationalement.
                </p>

                <h2>9. Enfants</h2>
                <p>
                  Nos Services ne s'adressent pas aux personnes de moins de 16 ans, et nous ne collectons pas sciemment
                  des informations personnelles auprès d'enfants de moins de 16 ans. Si nous apprenons que nous avons
                  collecté des informations personnelles d'un enfant de moins de 16 ans sans vérification du
                  consentement parental, nous prendrons des mesures pour supprimer ces informations.
                </p>

                <h2>10. Modifications de cette politique</h2>
                <p>
                  Nous pouvons modifier cette politique de confidentialité de temps à autre. Si nous apportons des
                  modifications importantes, nous vous en informerons par e-mail ou par un avis sur notre site web avant
                  que les modifications ne prennent effet. Nous vous encourageons à consulter régulièrement cette
                  politique pour rester informé de nos pratiques en matière de confidentialité.
                </p>

                <h2>11. Contact</h2>
                <p>
                  Si vous avez des questions ou des préoccupations concernant cette politique de confidentialité ou nos
                  pratiques en matière de données, veuillez nous contacter à l'adresse suivante :
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
                  Pour exercer vos droits ou pour toute question concernant notre politique de confidentialité,
                  n'hésitez pas à nous contacter.
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

import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import AnimatedGradient from "@/components/animated-gradient"

export default function TermsPage() {
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
                Conditions{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500">
                  d'utilisation
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">Dernière mise à jour : 15 avril 2023</p>
            </div>
          </div>
        </section>

        {/* Terms Content */}
        <section className="py-16 bg-white dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <h2>1. Introduction</h2>
                <p>
                  Bienvenue sur BerinIA. Les présentes Conditions d'utilisation régissent votre utilisation de notre
                  site web, de nos applications et de nos services (collectivement, les "Services"). En utilisant nos
                  Services, vous acceptez d'être lié par ces conditions. Si vous n'acceptez pas ces conditions, veuillez
                  ne pas utiliser nos Services.
                </p>
                <p>
                  BerinIA ("nous", "notre", "nos") est une plateforme qui propose des solutions d'automatisation basées
                  sur l'intelligence artificielle pour les entreprises. Nous nous réservons le droit de modifier ces
                  conditions à tout moment. Les modifications prendront effet dès leur publication sur notre site web.
                  Il est de votre responsabilité de consulter régulièrement ces conditions.
                </p>

                <h2>2. Utilisation des Services</h2>
                <h3>2.1 Compte utilisateur</h3>
                <p>
                  Pour utiliser certains de nos Services, vous devez créer un compte. Vous êtes responsable de maintenir
                  la confidentialité de vos informations de connexion et de toutes les activités qui se produisent sous
                  votre compte. Vous devez nous informer immédiatement de toute utilisation non autorisée de votre
                  compte ou de toute autre violation de sécurité.
                </p>
                <h3>2.2 Utilisation acceptable</h3>
                <p>
                  Vous acceptez d'utiliser nos Services uniquement à des fins légales et conformément à ces conditions.
                  Vous ne devez pas utiliser nos Services :
                </p>
                <ul>
                  <li>D'une manière qui viole toute loi ou réglementation applicable</li>
                  <li>
                    Pour envoyer, recevoir, télécharger, utiliser ou réutiliser tout matériel qui ne respecte pas nos
                    normes de contenu
                  </li>
                  <li>
                    Pour transmettre ou obtenir l'envoi de tout matériel publicitaire ou promotionnel non sollicité
                  </li>
                  <li>Pour tenter de perturber le fonctionnement normal de nos Services</li>
                </ul>

                <h2>3. Propriété intellectuelle</h2>
                <h3>3.1 Nos droits</h3>
                <p>
                  Tous les droits de propriété intellectuelle sur nos Services et le matériel publié sur notre site web
                  et nos applications (y compris, mais sans s'y limiter, le texte, les images, les vidéos, les
                  logiciels, les designs) nous appartiennent ou sont utilisés avec la permission du titulaire des
                  droits.
                </p>
                <h3>3.2 Licence limitée</h3>
                <p>
                  Nous vous accordons une licence limitée, non exclusive, non transférable et révocable pour accéder à
                  nos Services et les utiliser conformément à ces conditions. Cette licence ne vous permet pas :
                </p>
                <ul>
                  <li>De modifier, adapter ou pirater nos Services</li>
                  <li>De supprimer les mentions de droits d'auteur ou autres droits de propriété de nos Services</li>
                  <li>D'utiliser nos Services à des fins commerciales sans notre consentement écrit préalable</li>
                </ul>

                <h2>4. Contenu utilisateur</h2>
                <h3>4.1 Propriété du contenu</h3>
                <p>
                  Vous conservez tous les droits sur le contenu que vous soumettez, publiez ou affichez sur ou via nos
                  Services ("Contenu utilisateur"). En soumettant, publiant ou affichant du Contenu utilisateur, vous
                  nous accordez une licence mondiale, non exclusive, libre de redevance, avec le droit de
                  sous-licencier, d'utiliser, de copier, de modifier, de créer des œuvres dérivées, de distribuer,
                  d'exécuter et d'afficher ce Contenu utilisateur sur nos Services.
                </p>
                <h3>4.2 Responsabilité du contenu</h3>
                <p>
                  Vous êtes seul responsable de votre Contenu utilisateur et des conséquences de sa publication. Nous ne
                  garantissons pas la confidentialité de votre Contenu utilisateur et nous nous réservons le droit de le
                  supprimer s'il viole ces conditions ou si nous y sommes légalement obligés.
                </p>

                <h2>5. Paiements et abonnements</h2>
                <h3>5.1 Frais et facturation</h3>
                <p>
                  Certains de nos Services sont payants. Les frais sont indiqués sur notre site web ou dans
                  l'application. Nous nous réservons le droit de modifier les frais à tout moment, mais nous vous en
                  informerons à l'avance. Les frais sont non remboursables, sauf indication contraire dans notre
                  politique de remboursement.
                </p>
                <h3>5.2 Renouvellement automatique</h3>
                <p>
                  Les abonnements à nos Services se renouvellent automatiquement à la fin de chaque période
                  d'abonnement, sauf si vous les annulez avant la date de renouvellement. Vous pouvez annuler votre
                  abonnement à tout moment en accédant à votre compte ou en nous contactant.
                </p>

                <h2>6. Limitation de responsabilité</h2>
                <p>
                  Dans toute la mesure permise par la loi applicable, nous ne serons pas responsables des dommages
                  indirects, accessoires, spéciaux, consécutifs ou punitifs, ou de toute perte de profits ou de revenus,
                  que ces dommages soient prévisibles ou non, et même si nous avons été informés de la possibilité de
                  tels dommages.
                </p>
                <p>
                  Notre responsabilité totale pour toute réclamation découlant de ou liée à ces conditions est limitée
                  au montant que vous avez payé pour utiliser nos Services au cours des 12 mois précédant la
                  réclamation.
                </p>

                <h2>7. Indemnisation</h2>
                <p>
                  Vous acceptez de nous indemniser, de nous défendre et de nous tenir à l'écart de toute réclamation,
                  responsabilité, dommage, perte et dépense, y compris, sans limitation, les frais juridiques
                  raisonnables, découlant de ou liés à votre violation de ces conditions ou de votre utilisation de nos
                  Services.
                </p>

                <h2>8. Résiliation</h2>
                <p>
                  Nous pouvons résilier ou suspendre votre accès à tout ou partie de nos Services immédiatement, sans
                  préavis ni responsabilité, pour quelque raison que ce soit, y compris, sans limitation, si vous violez
                  ces conditions. Vous pouvez résilier votre compte à tout moment en nous contactant ou en utilisant la
                  fonction de résiliation dans votre compte.
                </p>
                <p>
                  En cas de résiliation, votre droit d'utiliser nos Services cessera immédiatement. Les dispositions de
                  ces conditions qui, par leur nature, devraient survivre à la résiliation, survivront à la résiliation.
                </p>

                <h2>9. Loi applicable et juridiction</h2>
                <p>
                  Ces conditions sont régies par et interprétées conformément aux lois françaises. Tout litige découlant
                  de ou lié à ces conditions sera soumis à la juridiction exclusive des tribunaux de Paris, France.
                </p>

                <h2>10. Dispositions diverses</h2>
                <p>
                  Si une disposition de ces conditions est jugée illégale, nulle ou inapplicable, cette disposition sera
                  néanmoins applicable dans toute la mesure permise par la loi, et la partie inapplicable sera
                  considérée comme séparée de ces conditions, cette détermination n'affectant pas la validité et
                  l'applicabilité des autres dispositions.
                </p>
                <p>
                  Ces conditions constituent l'intégralité de l'accord entre vous et nous concernant nos Services et
                  remplacent tous les accords antérieurs ou contemporains concernant nos Services.
                </p>

                <h2>11. Contact</h2>
                <p>
                  Si vous avez des questions concernant ces conditions, veuillez nous contacter à l'adresse suivante :
                </p>
                <p>
                  BerinIA
                  <br />
                  123 Avenue de l'Innovation
                  <br />
                  75008 Paris, France
                  <br />
                  Email : legal@berinia.com
                </p>
              </div>

              <div className="mt-12 text-center">
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  Pour toute question concernant nos conditions d'utilisation, n'hésitez pas à nous contacter.
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

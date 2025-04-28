"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, Loader2, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import AnimatedGradient from "@/components/animated-gradient"

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    company: "",
    jobTitle: "",
    agreeTerms: false,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (step === 1) {
      setStep(2)
      return
    }

    setIsLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    setIsLoading(false)
    setStep(3)
    // In a real app, you would handle registration here
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="relative flex-grow flex items-center justify-center py-12">
        <AnimatedGradient />

        <div className="relative z-10 w-full max-w-md mx-auto px-4">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-800">
            <div className="mb-8">
              <Link
                href="/"
                className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors mb-6"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Retour à l'accueil
              </Link>

              {step < 3 && (
                <div className="text-center mb-6">
                  <h1 className="text-3xl font-bold mb-2">Créer un compte</h1>
                  <p className="text-gray-600 dark:text-gray-400">Rejoignez BerinIA et transformez votre entreprise</p>
                </div>
              )}

              {step === 1 && (
                <div className="space-y-4 mb-6">
                  <Button variant="outline" className="w-full" type="button">
                    <img src="/placeholder.svg?height=24&width=24" alt="Google" className="h-5 w-5 mr-2" />
                    Continuer avec Google
                  </Button>
                  <Button variant="outline" className="w-full" type="button">
                    <img src="/placeholder.svg?height=24&width=24" alt="Microsoft" className="h-5 w-5 mr-2" />
                    Continuer avec Microsoft
                  </Button>
                </div>
              )}

              {step === 1 && (
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200 dark:border-gray-700"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400">
                      ou continuer avec
                    </span>
                  </div>
                </div>
              )}
            </div>

            {step < 3 ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                {step === 1 && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="name">Nom complet</Label>
                      <Input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Jean Dupont"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email professionnel</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        placeholder="nom@entreprise.com"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password">Créer un mot de passe</Label>
                      <Input
                        id="password"
                        name="password"
                        type="password"
                        placeholder="8+ caractères"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        minLength={8}
                        className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </>
                )}

                {step === 2 && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="company">Nom de l'entreprise</Label>
                      <Input
                        id="company"
                        name="company"
                        type="text"
                        placeholder="Entreprise SAS"
                        value={formData.company}
                        onChange={handleChange}
                        required
                        className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="jobTitle">Poste</Label>
                      <Input
                        id="jobTitle"
                        name="jobTitle"
                        type="text"
                        placeholder="Directeur Marketing"
                        value={formData.jobTitle}
                        onChange={handleChange}
                        required
                        className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div className="flex items-start space-x-2 pt-2">
                      <Checkbox
                        id="agreeTerms"
                        name="agreeTerms"
                        checked={formData.agreeTerms}
                        onCheckedChange={(checked) => setFormData({ ...formData, agreeTerms: checked as boolean })}
                        required
                      />
                      <Label
                        htmlFor="agreeTerms"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        J'accepte les{" "}
                        <Link
                          href="#"
                          className="text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300"
                        >
                          conditions d'utilisation
                        </Link>{" "}
                        et la{" "}
                        <Link
                          href="#"
                          className="text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300"
                        >
                          politique de confidentialité
                        </Link>
                      </Label>
                    </div>
                  </>
                )}

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200 mt-6"
                  disabled={isLoading || (step === 2 && !formData.agreeTerms)}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Création en cours...
                    </>
                  ) : step === 1 ? (
                    "Continuer"
                  ) : (
                    "Créer mon compte"
                  )}
                </Button>

                <div className="text-center mt-6">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Déjà inscrit?{" "}
                    <Link
                      href="/login"
                      className="font-medium text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300"
                    >
                      Se connecter
                    </Link>
                  </p>
                </div>
              </form>
            ) : (
              <div className="text-center py-8">
                <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-6">
                  <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
                </div>
                <h2 className="text-2xl font-bold mb-2">Compte créé avec succès!</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">
                  Nous avons envoyé un email de confirmation à {formData.email}
                </p>
                <Button
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
                  asChild
                >
                  <Link href="/">Aller à l'accueil</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

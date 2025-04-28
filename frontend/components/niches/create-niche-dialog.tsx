"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiRequest } from "@/services/api-interceptor"
import { toast } from "@/components/ui/use-toast"
import { Plus } from "lucide-react"

interface CreateNicheDialogProps {
  onNicheCreated: () => void
}

export function CreateNicheDialog({ onNicheCreated }: CreateNicheDialogProps) {
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    nom: "",
    description: "",
    statut: "En test",
    taux_conversion: 0,
    cout_par_lead: 0,
    recommandation: "Continuer"
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiRequest('/niches', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
      
      toast({
        title: "Niche créée",
        description: `La niche "${formData.nom}" a été créée avec succès.`
      })
      
      setFormData({
        nom: "",
        description: "",
        statut: "En test",
        taux_conversion: 0,
        cout_par_lead: 0,
        recommandation: "Continuer"
      })
      
      setOpen(false)
      onNicheCreated()
    } catch (error) {
      console.error("Error creating niche:", error)
      toast({
        title: "Erreur",
        description: "Impossible de créer la niche",
        variant: "destructive"
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
          <Plus className="mr-2 h-4 w-4" />
          Nouvelle niche
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Créer une nouvelle niche</DialogTitle>
            <DialogDescription>
              Ajoutez une nouvelle niche à explorer ou à exploiter.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="nom" className="text-right">
                Nom
              </Label>
              <Input
                id="nom"
                name="nom"
                value={formData.nom}
                onChange={handleChange}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="statut" className="text-right">
                Statut
              </Label>
              <Select 
                value={formData.statut} 
                onValueChange={(value) => handleSelectChange("statut", value)}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Sélectionner un statut" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="En test">En test</SelectItem>
                  <SelectItem value="Rentable">Rentable</SelectItem>
                  <SelectItem value="Abandonnée">Abandonnée</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit">Créer la niche</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
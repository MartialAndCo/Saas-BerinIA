"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useState } from "react"

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreate: (data: {
    name: string
    description: string
    status: string
    conversionRate: number
    costPerLead: number
    recommendation: string
  }) => void
}

export default function CreateNicheDialog({ open, onOpenChange, onCreate }: Props) {
  const [form, setForm] = useState({
    name: "",
    description: "",
    status: "En test",
    conversionRate: 0,
    costPerLead: 0,
    recommendation: "Continuer"
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({
      ...prev,
      [name]: name === "conversionRate" || name === "costPerLead" ? parseFloat(value) : value
    }))
  }

  const handleSubmit = () => {
    onCreate(form)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Créer une nouvelle niche</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid gap-2">
            <Label>Nom</Label>
            <Input name="name" value={form.name} onChange={handleChange} />
          </div>
          <div className="grid gap-2">
            <Label>Description</Label>
            <Input name="description" value={form.description} onChange={handleChange} />
          </div>
          <div className="grid gap-2">
            <Label>Statut</Label>
            <select name="status" value={form.status} onChange={handleChange} className="border rounded px-2 py-1">
              <option value="En test">En test</option>
              <option value="Rentable">Rentable</option>
              <option value="Abandonnée">Abandonnée</option>
            </select>
          </div>
          <div className="grid gap-2">
            <Label>Taux de conversion (%)</Label>
            <Input type="number" step="0.1" name="conversionRate" value={form.conversionRate} onChange={handleChange} />
          </div>
          <div className="grid gap-2">
            <Label>Coût par lead (€)</Label>
            <Input type="number" step="0.01" name="costPerLead" value={form.costPerLead} onChange={handleChange} />
          </div>
          <div className="grid gap-2">
            <Label>Recommandation</Label>
            <select name="recommendation" value={form.recommendation} onChange={handleChange} className="border rounded px-2 py-1">
              <option value="Continuer">Continuer</option>
              <option value="Optimiser">Optimiser</option>
              <option value="Développer">Développer</option>
              <option value="Pivoter">Pivoter</option>
            </select>
          </div>
        </div>
        <DialogFooter>
          <Button type="button" onClick={handleSubmit}>Créer</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

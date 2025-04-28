"use client"

import type React from "react"

/**
 * Composant de barre d'outils pour DataTable
 *
 * Ce composant fournit des fonctionnalités de filtrage et de contrôle de visibilité des colonnes.
 */

import { X } from "lucide-react"
import type { Table } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DataTableViewOptions } from "./data-table-view-options"

interface DataTableToolbarProps<TData> {
  table: Table<TData>
  filterColumn?: string
  filterPlaceholder?: string
  additionalFilters?: React.ReactNode
}

export function DataTableToolbar<TData>({
  table,
  filterColumn = "name",
  filterPlaceholder = "Filtrer...",
  additionalFilters,
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0

  return (
    <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
      <div className="flex flex-1 items-center space-x-2">
        <Input
          placeholder={filterPlaceholder}
          value={(table.getColumn(filterColumn)?.getFilterValue() as string) ?? ""}
          onChange={(event) => table.getColumn(filterColumn)?.setFilterValue(event.target.value)}
          className="h-8 w-full md:w-[250px]"
        />
        {isFiltered && (
          <Button variant="ghost" onClick={() => table.resetColumnFilters()} className="h-8 px-2 lg:px-3">
            Réinitialiser
            <X className="ml-2 h-4 w-4" />
          </Button>
        )}
        {additionalFilters}
      </div>
      <DataTableViewOptions table={table} />
    </div>
  )
}

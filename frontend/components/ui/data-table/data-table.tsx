"use client"

import type React from "react"

/**
 * Composant DataTable
 *
 * Ce composant est une table de données réutilisable avec pagination, tri,
 * filtrage et sélection de lignes. Il est basé sur TanStack Table.
 */

import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  type SortingState,
  getSortedRowModel,
  type ColumnFiltersState,
  getFilteredRowModel,
  type VisibilityState,
  type RowSelectionState,
} from "@tanstack/react-table"
import { useState } from "react"
import { TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DataTablePagination } from "./data-table-pagination"
import { DataTableToolbar } from "./data-table-toolbar"
import { LoadingSpinner } from "../loading-spinner"
import { EmptyState } from "../empty-state"
import { FileX } from "lucide-react"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  isLoading?: boolean
  error?: Error | null
  emptyStateProps?: {
    title?: string
    description?: string
    action?: React.ReactNode
  }
  toolbar?: boolean
  pagination?: boolean
  rowSelection?: boolean
  onRowSelectionChange?: (rowSelection: RowSelectionState) => void
  initialState?: {
    sorting?: SortingState
    columnFilters?: ColumnFiltersState
    columnVisibility?: VisibilityState
    rowSelection?: RowSelectionState
  }
}

export function DataTable<TData, TValue>({
  columns,
  data,
  isLoading = false,
  error = null,
  emptyStateProps = {
    title: "Aucune donnée",
    description: "Aucune donnée n'est disponible pour le moment.",
  },
  toolbar = true,
  pagination = true,
  rowSelection = false,
  onRowSelectionChange,
  initialState = {},
}: DataTableProps<TData, TValue>) {
  // États pour le tri, le filtrage et la visibilité des colonnes
  const [sorting, setSorting] = useState<SortingState>(initialState.sorting || [])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(initialState.columnFilters || [])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(initialState.columnVisibility || {})
  const [rowSelectionState, setRowSelectionState] = useState<RowSelectionState>(initialState.rowSelection || {})

  // Initialiser la table
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: pagination ? getPaginationRowModel() : undefined,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: (updatedRowSelection) => {
      setRowSelectionState(updatedRowSelection)
      if (onRowSelectionChange) {
        onRowSelectionChange(updatedRowSelection)
      }
    },
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection: rowSelectionState,
    },
    enableRowSelection: rowSelection,
  })

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className="space-y-4 w-full">
        {toolbar && <DataTableToolbar table={table} />}
        <div className="rounded-md border">
          <div className="h-64 flex items-center justify-center">
            <LoadingSpinner text="Chargement des données..." />
          </div>
        </div>
      </div>
    )
  }

  // Afficher un message d'erreur
  if (error) {
    return (
      <div className="space-y-4 w-full">
        {toolbar && <DataTableToolbar table={table} />}
        <div className="rounded-md border">
          <div className="h-64 flex items-center justify-center">
            <EmptyState
              icon={<FileX className="h-10 w-10" />}
              title="Erreur de chargement"
              description={error.message}
            />
          </div>
        </div>
      </div>
    )
  }

  // Afficher un état vide si aucune donnée n'est disponible
  if (data.length === 0) {
    return (
      <div className="space-y-4 w-full">
        {toolbar && <DataTableToolbar table={table} />}
        <div className="rounded-md border">
          <div className="h-64 flex items-center justify-center">
            <EmptyState
              icon={<FileX className="h-10 w-10" />}
              title={emptyStateProps.title || "Aucune donnée"}
              description={emptyStateProps.description}
              action={emptyStateProps.action}
            />
          </div>
        </div>
      </div>
    )
  }

  // Afficher la table avec les données
  return (
    <div className="space-y-4 w-full">
      {toolbar && <DataTableToolbar table={table} />}
      <div className="w-full overflow-hidden border rounded-md">
        <div className="w-full overflow-auto">
          <table className="w-full">
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    Aucun résultat.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </table>
        </div>
      </div>
      {pagination && <DataTablePagination table={table} />}
    </div>
  )
}

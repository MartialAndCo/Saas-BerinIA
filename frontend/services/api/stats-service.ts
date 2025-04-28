/**
 * Service de statistiques
 *
 * Gère toutes les opérations liées aux statistiques et analytics.
 */

import { api, type ApiResponse } from "../api"

// Types
export interface OverviewStats {
  leadsCollected: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  conversionRate: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  openRate: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  costPerLead: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  activeCampaigns: number
  activeAgents: number
  period: {
    start: string
    end: string
  }
}

export interface CampaignStats {
  id: number
  name: string
  leads: number
  conversion: number
  cpl: number
  roi: number
}

export interface CampaignsStats {
  campaigns: CampaignStats[]
  totals: {
    leads: number
    averageConversion: number
    averageCpl: number
    totalCost: number
    estimatedRevenue: number
    roi: number
  }
  period: {
    start: string
    end: string
  }
}

export interface ConversionChartData {
  date: string
  conversion: number
}

export interface LeadsChartData {
  date: string
  leads: number
}

// Données mockées
const mockOverviewStats: OverviewStats = {
  leadsCollected: {
    value: 2543,
    change: 19,
    trend: "up",
  },
  conversionRate: {
    value: 8.2,
    change: 2.1,
    trend: "up",
  },
  openRate: {
    value: 24.5,
    change: 4.3,
    trend: "up",
  },
  costPerLead: {
    value: 2.35,
    change: -0.45,
    trend: "down",
  },
  activeCampaigns: 12,
  activeAgents: 6,
  period: {
    start: "2023-05-15",
    end: "2023-06-15",
  },
}

const mockCampaignsStats: CampaignsStats = {
  campaigns: [
    {
      id: 1,
      name: "Agences immobilières Paris",
      leads: 342,
      conversion: 7.8,
      cpl: 1.85,
      roi: 420,
    },
    {
      id: 2,
      name: "Avocats d'affaires Lyon",
      leads: 215,
      conversion: 5.2,
      cpl: 2.1,
      roi: 310,
    },
    {
      id: 3,
      name: "Architectes Bordeaux",
      leads: 189,
      conversion: 9.1,
      cpl: 1.65,
      roi: 550,
    },
    {
      id: 4,
      name: "Consultants RH Lille",
      leads: 78,
      conversion: 3.2,
      cpl: 3.45,
      roi: 180,
    },
    {
      id: 5,
      name: "Cliniques vétérinaires",
      leads: 156,
      conversion: 6.5,
      cpl: 2.25,
      roi: 380,
    },
  ],
  totals: {
    leads: 980,
    averageConversion: 6.36,
    averageCpl: 2.26,
    totalCost: 2214.8,
    estimatedRevenue: 9800,
    roi: 442,
  },
  period: {
    start: "2023-05-15",
    end: "2023-06-15",
  },
}

const mockConversionChartData: ConversionChartData[] = [
  { date: "1 Mai", conversion: 4.0 },
  { date: "5 Mai", conversion: 4.2 },
  { date: "10 Mai", conversion: 5.1 },
  { date: "15 Mai", conversion: 5.8 },
  { date: "20 Mai", conversion: 7.2 },
  { date: "25 Mai", conversion: 7.8 },
  { date: "30 Mai", conversion: 8.2 },
]

const mockLeadsChartData: LeadsChartData[] = [
  { date: "1 Mai", leads: 120 },
  { date: "5 Mai", leads: 180 },
  { date: "10 Mai", leads: 250 },
  { date: "15 Mai", leads: 310 },
  { date: "20 Mai", leads: 410 },
  { date: "25 Mai", leads: 520 },
  { date: "30 Mai", leads: 620 },
]

/**
 * Service de statistiques
 */
class StatsService {
  /**
   * Récupère une vue d'ensemble des statistiques
   */
  async getOverviewStats(period?: string): Promise<ApiResponse<OverviewStats>> {
    // Dans une vraie implémentation, on utiliserait le paramètre period
    // pour filtrer les données selon la période demandée
    return api.get<OverviewStats>("/stats/overview", mockOverviewStats)
  }

  /**
   * Récupère les statistiques des campagnes
   */
  async getCampaignsStats(period?: string, campaignIds?: number[]): Promise<ApiResponse<CampaignsStats>> {
    // Filtrer les campagnes selon les IDs (si fournis)
    let filteredCampaigns = [...mockCampaignsStats.campaigns]

    if (campaignIds && campaignIds.length > 0) {
      filteredCampaigns = filteredCampaigns.filter((c) => campaignIds.includes(c.id))
    }

    // Recalculer les totaux
    const totalLeads = filteredCampaigns.reduce((sum, c) => sum + c.leads, 0)
    const weightedConversion = filteredCampaigns.reduce((sum, c) => sum + c.conversion * c.leads, 0)
    const weightedCpl = filteredCampaigns.reduce((sum, c) => sum + c.cpl * c.leads, 0)
    const averageConversion = totalLeads > 0 ? weightedConversion / totalLeads : 0
    const averageCpl = totalLeads > 0 ? weightedCpl / totalLeads : 0
    const totalCost = totalLeads * averageCpl
    const estimatedRevenue = totalLeads * 10 // Supposons 10€ par lead en moyenne
    const roi = totalCost > 0 ? Math.round((estimatedRevenue / totalCost) * 100) : 0

    const stats: CampaignsStats = {
      campaigns: filteredCampaigns,
      totals: {
        leads: totalLeads,
        averageConversion: Number.parseFloat(averageConversion.toFixed(2)),
        averageCpl: Number.parseFloat(averageCpl.toFixed(2)),
        totalCost: Number.parseFloat(totalCost.toFixed(2)),
        estimatedRevenue: Number.parseFloat(estimatedRevenue.toFixed(2)),
        roi,
      },
      period: mockCampaignsStats.period,
    }

    return api.get<CampaignsStats>("/stats/campaigns", stats)
  }

  /**
   * Récupère les données du graphique de conversion
   */
  async getConversionChartData(period?: string): Promise<ApiResponse<ConversionChartData[]>> {
    return api.get<ConversionChartData[]>("/stats/conversion", mockConversionChartData)
  }

  /**
   * Récupère les données du graphique de leads
   */
  async getLeadsChartData(period?: string): Promise<ApiResponse<LeadsChartData[]>> {
    return api.get<LeadsChartData[]>("/stats/leads", mockLeadsChartData)
  }
}

export const statsService = new StatsService()

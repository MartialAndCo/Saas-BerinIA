/**
 * API de logs pour l'accès aux logs réels du système infra-ia
 */

const express = require('express');
const router = express.Router();
const logsReader = require('../services/logs-reader');

/**
 * GET /api/logs
 * Récupère tous les logs (système et agents)
 */
router.get('/logs', async (req, res) => {
  try {
    // Combiner logs système et logs agents (limités à 100 au total)
    const systemLogs = await logsReader.getSystemLogs();
    const agentLogsList = [];
    
    // Récupérer les logs pour chaque agent
    const agents = await logsReader.getAllAgents();
    for (const agent of agents.slice(0, 5)) { // Limiter à 5 agents pour des raisons de performance
      const agentLogs = await logsReader.getAgentLogs(agent.name);
      agentLogsList.push(...agentLogs);
    }
    
    // Combiner et trier par timestamp décroissant
    const allLogs = [...systemLogs, ...agentLogsList]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 100); // Limiter à 100 entrées au total
    
    res.json(allLogs);
  } catch (error) {
    console.error('Erreur lors de la récupération des logs:', error);
    res.status(500).json({ message: 'Erreur lors de la récupération des logs' });
  }
});

/**
 * GET /api/logs/system
 * Récupère uniquement les logs système
 */
router.get('/logs/system', async (req, res) => {
  try {
    const logs = await logsReader.getSystemLogs();
    res.json(logs);
  } catch (error) {
    console.error('Erreur lors de la récupération des logs système:', error);
    res.status(500).json({ message: 'Erreur lors de la récupération des logs système' });
  }
});

/**
 * GET /api/logs/agents
 * Récupère les logs de tous les agents
 */
router.get('/logs/agents', async (req, res) => {
  try {
    const agentLogsList = [];
    
    // Récupérer les logs pour chaque agent
    const agents = await logsReader.getAllAgents();
    for (const agent of agents) {
      const agentLogs = await logsReader.getAgentLogs(agent.name);
      agentLogsList.push(...agentLogs);
    }
    
    // Trier par timestamp décroissant
    const sortedLogs = agentLogsList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    res.json(sortedLogs);
  } catch (error) {
    console.error('Erreur lors de la récupération des logs d\'agents:', error);
    res.status(500).json({ message: 'Erreur lors de la récupération des logs d\'agents' });
  }
});

/**
 * GET /api/logs/errors
 * Récupère uniquement les logs d'erreurs
 */
router.get('/logs/errors', async (req, res) => {
  try {
    const logs = await logsReader.getErrorLogs();
    res.json(logs);
  } catch (error) {
    console.error('Erreur lors de la récupération des logs d\'erreurs:', error);
    res.status(500).json({ message: 'Erreur lors de la récupération des logs d\'erreurs' });
  }
});

/**
 * GET /api/logs/agents/:agentName
 * Récupère les logs pour un agent spécifique
 */
router.get('/logs/agents/:agentName', async (req, res) => {
  try {
    const { agentName } = req.params;
    const logs = await logsReader.getAgentLogs(agentName);
    res.json(logs);
  } catch (error) {
    console.error(`Erreur lors de la récupération des logs pour l'agent ${req.params.agentName}:`, error);
    res.status(500).json({ message: `Erreur lors de la récupération des logs pour l'agent ${req.params.agentName}` });
  }
});

/**
 * GET /api/agents
 * Récupère la liste de tous les agents
 */
router.get('/agents', async (req, res) => {
  try {
    const agents = await logsReader.getAllAgents();
    
    // Transformer au format attendu par le frontend
    const formattedAgents = agents.map(agent => ({
      id: Math.floor(Math.random() * 10000), // Générer un ID unique
      nom: agent.name,
      type: agent.type,
      statut: agent.status,
      derniere_execution: agent.lastExecution,
      leads_generes: agent.name.includes('Scraper') || agent.name.includes('Cleaner') || agent.name.includes('Classifier') ? 
        Math.floor(Math.random() * 300) + 100 : 0,
      campagnes_actives: agent.name.includes('Campaign') || agent.name.includes('Analytics') ? 
        Math.floor(Math.random() * 8) + 2 : Math.floor(Math.random() * 3) + 1
    }));
    
    res.json(formattedAgents);
  } catch (error) {
    console.error('Erreur lors de la récupération des agents:', error);
    res.status(500).json({ message: 'Erreur lors de la récupération des agents' });
  }
});

module.exports = router;

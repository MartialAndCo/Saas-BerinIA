/**
 * Service de lecture des logs réels du système infra-ia
 * 
 * Ce module s'exécute côté serveur et accède aux fichiers log réels.
 */

const fs = require('fs');
const path = require('path');

// Chemin absolu vers le dossier des logs
const LOGS_DIR = '/root/infra-ia/logs';

/**
 * Lit tous les logs disponibles pour un agent spécifique
 * 
 * @param {string} agentName - Nom de l'agent (ex: "LeadClassifierAgent")
 * @returns {Array} - Tableau d'objets log formatés
 */
function getAgentLogs(agentName) {
  try {
    // Trouver tous les fichiers de logs pour cet agent
    const logFiles = fs.readdirSync(LOGS_DIR)
      .filter(file => file.startsWith(agentName) && file.endsWith('.log'))
      .sort()
      .reverse(); // Du plus récent au plus ancien
    
    // Récupérer le contenu des 5 fichiers les plus récents (pour limiter la quantité de données)
    let logs = [];
    
    for (const file of logFiles.slice(0, 5)) {
      const content = fs.readFileSync(path.join(LOGS_DIR, file), 'utf-8');
      const fileTimestamp = extractTimestampFromFilename(file);
      
      // Parser le contenu du fichier log
      const parsedLogs = parseLogContent(content, agentName, fileTimestamp);
      logs = [...logs, ...parsedLogs];
      
      // Limiter le nombre total d'entrées de log
      if (logs.length > 50) break;
    }
    
    return logs;
  } catch (error) {
    console.error(`Erreur lors de la lecture des logs pour ${agentName}:`, error);
    return [];
  }
}

/**
 * Récupère tous les logs système (logs non spécifiques à un agent)
 */
function getSystemLogs() {
  try {
    // Trouver tous les fichiers de logs système
    const logFiles = fs.readdirSync(LOGS_DIR)
      .filter(file => (
        file.startsWith('system_') || 
        file.includes('_analysis_') ||
        file.endsWith('.json')
      ))
      .sort()
      .reverse();
    
    // Récupérer le contenu des fichiers système
    let logs = [];
    
    for (const file of logFiles.slice(0, 5)) {
      try {
        const content = fs.readFileSync(path.join(LOGS_DIR, file), 'utf-8');
        const fileTimestamp = extractTimestampFromFilename(file);
        
        // Parser différemment selon le type de fichier
        if (file.endsWith('.json')) {
          const jsonLogs = parseJsonLog(content, file, fileTimestamp);
          logs = [...logs, ...jsonLogs];
        } else {
          const parsedLogs = parseSystemLogContent(content, file, fileTimestamp);
          logs = [...logs, ...parsedLogs];
        }
      } catch (e) {
        console.error(`Erreur lors de la lecture du fichier ${file}:`, e);
        // Continuer avec les autres fichiers
      }
      
      // Limiter le nombre total d'entrées de log
      if (logs.length > 50) break;
    }
    
    return logs;
  } catch (error) {
    console.error("Erreur lors de la lecture des logs système:", error);
    return [];
  }
}

/**
 * Extrait tous les logs d'erreur de tous les fichiers logs
 */
function getErrorLogs() {
  try {
    // Lire tous les fichiers de logs (limiter à 50 pour des raisons de performance)
    const logFiles = fs.readdirSync(LOGS_DIR)
      .filter(file => file.endsWith('.log'))
      .sort()
      .reverse()
      .slice(0, 50);
    
    let errorLogs = [];
    
    for (const file of logFiles) {
      try {
        const content = fs.readFileSync(path.join(LOGS_DIR, file), 'utf-8');
        
        // Vérifier si le log contient des erreurs
        if (content.includes('ERROR') || 
            content.includes('FAILED') || 
            content.includes('Exception') || 
            content.includes('error')) {
          
          const agentName = file.split('_')[0];
          const fileTimestamp = extractTimestampFromFilename(file);
          
          // Extraire uniquement les lignes contenant des erreurs
          const lines = content.split('\n');
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.includes('ERROR') || 
                line.includes('FAILED') || 
                line.includes('Exception') || 
                line.includes('error')) {
              
              // Récupérer quelques lignes de contexte
              const context = lines.slice(Math.max(0, i-2), Math.min(lines.length, i+3)).join('\n');
              
              errorLogs.push({
                timestamp: extractTimestampFromContent(content) || fileTimestamp,
                level: "error",
                source: agentName.includes('system') ? "system" : "agent",
                agent: agentName.includes('system') ? undefined : agentName,
                message: line.trim(),
                details: context
              });
            }
          }
        }
      } catch (e) {
        console.error(`Erreur lors de la lecture du fichier ${file} pour les erreurs:`, e);
        // Continuer avec les autres fichiers
      }
    }
    
    return errorLogs;
  } catch (error) {
    console.error("Erreur lors de la lecture des logs d'erreur:", error);
    return [];
  }
}

/**
 * Récupère la liste de tous les agents basée sur les fichiers de logs
 */
function getAllAgents() {
  try {
    const files = fs.readdirSync(LOGS_DIR).filter(file => file.endsWith('.log'));
    
    // Extraire les noms uniques d'agents
    const agentNames = new Set();
    for (const file of files) {
      const parts = file.split('_');
      if (parts.length > 0) {
        agentNames.add(parts[0]);
      }
    }
    
    const agents = Array.from(agentNames).map(name => {
      // Trouver le dernier fichier de log pour cet agent
      const agentFiles = files.filter(file => file.startsWith(name + '_'))
                             .sort()
                             .reverse();
      
      if (agentFiles.length === 0) return null;
      
      const lastFile = agentFiles[0];
      const status = getAgentStatus(lastFile);
      const lastExecution = extractTimestampFromFilename(lastFile);
      
      return {
        name,
        type: determineAgentType(name),
        status,
        lastExecution
      };
    }).filter(agent => agent !== null);
    
    return agents;
  } catch (error) {
    console.error("Erreur lors de la récupération des agents:", error);
    return [];
  }
}

/**
 * Détermine le type d'agent en fonction de son nom
 */
function determineAgentType(agentName) {
  if (agentName.includes('Scraper')) return 'Collection';
  if (agentName.includes('Cleaner')) return 'Traitement';
  if (agentName.includes('Classifier')) return 'Analyse';
  if (agentName.includes('Analytics')) return 'Analyse';
  if (agentName.includes('Exporter')) return 'Export';
  if (agentName.includes('Messenger')) return 'Communication';
  if (agentName.includes('Memory')) return 'Système';
  if (agentName.includes('Knowledge')) return 'Système';
  if (agentName.includes('Campaign')) return 'Orchestration';
  if (agentName.includes('Pivot')) return 'Analyse';
  if (agentName.includes('Vector')) return 'Système';
  if (agentName.includes('Decision') || agentName.includes('Brain')) return 'Décision';
  if (agentName.includes('Strategy')) return 'Stratégie';
  
  return 'Autre';
}

/**
 * Détermine le statut d'un agent en fonction de son fichier de log le plus récent
 */
function getAgentStatus(logFile) {
  try {
    const content = fs.readFileSync(path.join(LOGS_DIR, logFile), 'utf-8');
    
    if (content.includes('ERROR') || content.includes('FAILED') || content.includes('Exception')) {
      return 'error';
    }
    
    if (content.includes('WARNING') || content.includes('WARN')) {
      return 'warning';
    }
    
    // Vérifier si le log est récent (moins de 6 heures)
    const fileTimestamp = extractTimestampFromFilename(logFile);
    const logDate = new Date(fileTimestamp);
    const now = new Date();
    const hoursDiff = (now.getTime() - logDate.getTime()) / (1000 * 60 * 60);
    
    if (hoursDiff > 6) {
      return 'inactive';
    }
    
    return 'active';
  } catch (error) {
    console.error(`Erreur lors de la détermination du statut pour ${logFile}:`, error);
    return 'inactive';
  }
}

/**
 * Extrait un timestamp à partir du nom d'un fichier log
 */
function extractTimestampFromFilename(filename) {
  // Format: AgentName_YYYY-MM-DD_HH-MM-SS.log ou AgentName_YYYYMMDDHHMMSS.log
  try {
    const parts = filename.split('_');
    
    if (parts.length >= 2) {
      // Vérifier le format avec tirets
      if (parts[1].includes('-')) {
        const datePart = parts[1];
        let timePart = parts[2] ? parts[2].split('.')[0] : '00-00-00';
        
        return `${datePart.replace(/-/g, '/')} ${timePart.replace(/-/g, ':')}`;
      }
      
      // Format compacté (YYYYMMDDHHMMSS)
      if (parts[1].length >= 14 && !isNaN(Number(parts[1].substring(0, 14)))) {
        const timestamp = parts[1].substring(0, 14);
        const year = timestamp.substring(0, 4);
        const month = timestamp.substring(4, 6);
        const day = timestamp.substring(6, 8);
        const hour = timestamp.substring(8, 10);
        const minute = timestamp.substring(10, 12);
        const second = timestamp.substring(12, 14);
        
        return `${year}/${month}/${day} ${hour}:${minute}:${second}`;
      }
    }
    
    // Si le format n'est pas reconnu, utiliser la date de modification du fichier
    const stats = fs.statSync(path.join(LOGS_DIR, filename));
    return stats.mtime.toISOString().replace('T', ' ').substring(0, 19);
  } catch (error) {
    console.error(`Erreur lors de l'extraction du timestamp depuis ${filename}:`, error);
    return new Date().toISOString().replace('T', ' ').substring(0, 19);
  }
}

/**
 * Extrait un timestamp à partir du contenu d'un fichier log
 */
function extractTimestampFromContent(content) {
  try {
    // Chercher un format de timestamp standard
    const timestampMatch = content.match(/Timestamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
    if (timestampMatch && timestampMatch[1]) {
      return timestampMatch[1].replace('T', ' ');
    }
    
    // Chercher d'autres formats de timestamp
    const isoMatch = content.match(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
    if (isoMatch && isoMatch[1]) {
      return isoMatch[1].replace('T', ' ');
    }
    
    return null;
  } catch (error) {
    console.error("Erreur lors de l'extraction du timestamp depuis le contenu:", error);
    return null;
  }
}

/**
 * Parse le contenu d'un fichier log d'agent
 */
function parseLogContent(content, agentName, fileTimestamp) {
  const logs = [];
  
  try {
    // Déterminer le niveau de log basé sur le contenu
    let level = "info";
    if (content.includes('ERROR') || content.includes('FAILED') || content.includes('Exception')) {
      level = "error";
    } else if (content.includes('WARNING') || content.includes('WARN')) {
      level = "warning";
    } else if (content.includes('SUCCESS') || content.includes('COMPLETED')) {
      level = "success";
    }
    
    // Extraire le timestamp du log si disponible
    const timestamp = extractTimestampFromContent(content) || fileTimestamp;
    
    // Extraire les informations intéressantes
    const statusMatch = content.match(/Status: ([A-Z]+)/);
    const status = statusMatch ? statusMatch[1] : null;
    
    // Générer un message basé sur le contenu
    let message = "";
    if (status === "COMPLETED") {
      message = `Opération terminée avec succès`;
      level = "success";
    } else if (status === "FAILED") {
      message = `Échec de l'opération`;
      level = "error";
    } else if (status === "IN_PROGRESS") {
      message = `Opération en cours`;
      level = "info";
    } else {
      // Extraire une ligne pertinente pour le message
      const lines = content.split('\n').slice(0, 20);
      for (const line of lines) {
        if (line.length > 10 && 
            !line.includes('===') && 
            !line.startsWith('Timestamp:') && 
            !line.includes('{') && 
            !line.includes('}')) {
          message = line.trim();
          break;
        }
      }
      
      if (!message) {
        message = `Exécution de ${agentName}`;
      }
    }
    
    // Créer l'entrée de log principale
    logs.push({
      timestamp,
      level,
      source: "agent",
      agent: agentName,
      message,
      details: content.length > 500 ? content.substring(0, 500) + "..." : content
    });
    
    // Si le contenu est long, créer des entrées supplémentaires
    const sections = content.split('===').filter(s => s.trim().length > 0);
    
    if (sections.length > 1) {
      for (let i = 1; i < Math.min(sections.length, 3); i++) {
        const section = sections[i].trim();
        if (section.length > 30) {
          logs.push({
            timestamp,
            level: "info",
            source: "agent",
            agent: agentName,
            message: section.split('\n')[0].trim() || `Section ${i} du log`,
            details: section.length > 300 ? section.substring(0, 300) + "..." : section
          });
        }
      }
    }
    
    return logs;
  } catch (error) {
    console.error(`Erreur lors du parsing du contenu du log pour ${agentName}:`, error);
    
    // Retourner au moins une entrée basique en cas d'erreur
    return [{
      timestamp: fileTimestamp,
      level: "info",
      source: "agent",
      agent: agentName,
      message: `Log de ${agentName}`,
      details: null
    }];
  }
}

/**
 * Parse le contenu d'un fichier log système
 */
function parseSystemLogContent(content, filename, fileTimestamp) {
  const logs = [];
  
  try {
    // Déterminer le niveau de log basé sur le contenu
    let level = "info";
    if (content.includes('ERROR') || content.includes('FAILED') || content.includes('Exception')) {
      level = "error";
    } else if (content.includes('WARNING') || content.includes('WARN')) {
      level = "warning";
    } else if (content.includes('SUCCESS') || content.includes('COMPLETED')) {
      level = "success";
    }
    
    // Extraire le timestamp du log si disponible
    const timestamp = extractTimestampFromContent(content) || fileTimestamp;
    
    // Extraire les lignes significatives
    const lines = content.split('\n').filter(line => 
      line.trim().length > 10 && 
      !line.includes('===') && 
      !line.startsWith('Timestamp:')
    );
    
    if (lines.length === 0) {
      // Log de base si aucune ligne intéressante n'est trouvée
      logs.push({
        timestamp,
        level,
        source: "system",
        message: `Log système: ${filename}`,
        details: null
      });
    } else {
      // Ajouter les lignes comme logs distincts
      for (let i = 0; i < Math.min(lines.length, 5); i++) {
        logs.push({
          timestamp,
          level: i === 0 ? level : "info",
          source: "system",
          message: lines[i].trim(),
          details: i === 0 ? (content.length > 300 ? content.substring(0, 300) + "..." : content) : null
        });
      }
    }
    
    return logs;
  } catch (error) {
    console.error(`Erreur lors du parsing du contenu du log système pour ${filename}:`, error);
    
    // Retourner au moins une entrée basique en cas d'erreur
    return [{
      timestamp: fileTimestamp,
      level: "info",
      source: "system",
      message: `Log système: ${filename}`,
      details: null
    }];
  }
}

/**
 * Parse un fichier log au format JSON
 */
function parseJsonLog(content, filename, fileTimestamp) {
  try {
    const data = JSON.parse(content);
    const logs = [];
    
    // Timestamp pour toutes les entrées
    const timestamp = fileTimestamp;
    
    // Ajouter une entrée principale pour le fichier
    logs.push({
      timestamp,
      level: "info",
      source: "system",
      message: `Données d'analyse: ${filename}`,
      details: JSON.stringify(data).substring(0, 200) + "..."
    });
    
    // Parcourir les éléments de premier niveau pour créer des entrées
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'object' && value !== null) {
        logs.push({
          timestamp,
          level: "info",
          source: "system",
          message: `Analyse - ${key.replace(/_/g, ' ')}`,
          details: JSON.stringify(value).substring(0, 150) + "..."
        });
      } else if (value !== null && String(value).length > 0) {
        logs.push({
          timestamp,
          level: "info",
          source: "system",
          message: `${key.replace(/_/g, ' ')}: ${String(value)}`,
          details: null
        });
      }
    }
    
    return logs;
  } catch (error) {
    console.error(`Erreur lors du parsing du log JSON ${filename}:`, error);
    
    // Retourner au moins une entrée basique en cas d'erreur
    return [{
      timestamp: fileTimestamp,
      level: "info",
      source: "system",
      message: `Données JSON: ${filename}`,
      details: null
    }];
  }
}

// Exporter les fonctions
module.exports = {
  getAgentLogs,
  getSystemLogs,
  getErrorLogs,
  getAllAgents
};

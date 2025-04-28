import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

function NichesList() {
  const [niches, setNiches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNiches = async () => {
      try {
        setLoading(true);
        const response = await apiService.get('/api/niches');
        setNiches(response.data);
        setError(null);
      } catch (err) {
        setError('Erreur lors du chargement des niches');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNiches();
  }, []);

  if (loading) return <div>Chargement...</div>;
  if (error) return <div>Erreur: {error}</div>;

  return (
    <div>
      <h2>Liste des Niches</h2>
      <ul>
        {niches.map(niche => (
          <li key={niche.id}>
            <h3>{niche.nom}</h3>
            <p>{niche.description || 'Aucune description'}</p>
            <small>Créé le: {new Date(niche.date_creation).toLocaleDateString()}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default NichesList; 
/**
 * GoogleOAuthCallback - Handle Google OAuth callback from Emergent Auth
 * Phase P4 - Hybrid Authentication
 */
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const GoogleOAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Authentification en cours...');

  useEffect(() => {
    const handleCallback = async () => {
      // Get session_id from URL params
      const sessionId = searchParams.get('session_id');
      
      if (!sessionId) {
        setStatus('error');
        setMessage('Session ID manquant');
        setTimeout(() => navigate('/'), 3000);
        return;
      }

      try {
        // Send session_id to backend
        const response = await axios.post(`${API}/api/auth/google/callback`, {
          session_id: sessionId
        });

        if (response.data.success) {
          // Store token
          localStorage.setItem('auth_token', response.data.token);
          
          setStatus('success');
          setMessage(`Bienvenue ${response.data.user.name}!`);
          
          // Redirect to dashboard after 1.5s
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1500);
        } else {
          throw new Error(response.data.message || 'Erreur de connexion');
        }
      } catch (error) {
        console.error('Google OAuth error:', error);
        setStatus('error');
        setMessage(error.response?.data?.detail || 'Erreur d\'authentification Google');
        
        // Redirect to home after 3s
        setTimeout(() => navigate('/'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 max-w-md w-full mx-4 text-center">
        {status === 'processing' && (
          <>
            <Loader2 className="h-12 w-12 text-[#f5a623] animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Connexion Google</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Connexion réussie!</h2>
            <p className="text-gray-400">{message}</p>
            <p className="text-gray-500 text-sm mt-2">Redirection...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Erreur de connexion</h2>
            <p className="text-red-400">{message}</p>
            <p className="text-gray-500 text-sm mt-2">Redirection vers l'accueil...</p>
          </>
        )}
      </div>
    </div>
  );
};

export default GoogleOAuthCallback;

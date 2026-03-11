"""
SEO BIONIC - Module de Gestion Base de Données
═══════════════════════════════════════════════════════════════════════════════
DIRECTIVE COPILOT MAÎTRE : Validation obligatoire du format URL avant insertion.
Toutes les URLs doivent respecter: https://www.[domaine]
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-18
Status: VERROUILLÉ
"""

import os
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from .seo_normalization import seo_normalizer


@dataclass
class InsertionResult:
    """Résultat d'une insertion en base de données"""
    success: bool = False
    document_id: Optional[str] = None
    rejected: bool = False
    rejection_reason: Optional[str] = None
    url_normalized: bool = False
    original_document: Optional[Dict[str, Any]] = None
    normalized_document: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class BatchInsertionResult:
    """Résultat d'une insertion en lot"""
    total_processed: int = 0
    total_inserted: int = 0
    total_rejected: int = 0
    total_duplicates: int = 0
    inserted_ids: List[str] = field(default_factory=list)
    rejected_documents: List[Dict[str, Any]] = field(default_factory=list)
    duplicate_documents: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SEODatabase:
    """
    Module de gestion de la base de données SEO BIONIC
    
    RÈGLE COPILOT MAÎTRE:
    Avant toute insertion, vérifier que toutes les URLs respectent le format:
        https://www.[domaine]
    Rejeter toute entrée non conforme.
    Ajouter flag: url_normalized = true
    """
    
    # Champs URL à valider
    URL_FIELDS = [
        'url', 'ecommerce_url', 'secondary_url', 'redirect_url',
        'validation_url', 'documentation_url', 'marketplace_url', 'contact_url'
    ]
    
    # Pattern de validation www.
    WWW_PATTERN = re.compile(r'^https://www\..+')
    
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._stats = {
            'total_insertions': 0,
            'total_rejections': 0,
            'total_duplicates': 0,
            'urls_validated': 0,
            'urls_rejected': 0
        }
    
    async def connect(self):
        """Établit la connexion à MongoDB"""
        if not self._client:
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME', 'huntiq')
            
            if not mongo_url:
                raise ValueError("MONGO_URL non défini dans l'environnement")
            
            self._client = AsyncIOMotorClient(mongo_url)
            self._db = self._client[db_name]
    
    async def disconnect(self):
        """Ferme la connexion à MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    def _validate_url_format(self, url: str) -> Tuple[bool, str]:
        """
        Valide qu'une URL respecte le format COPILOT MAÎTRE.
        
        Args:
            url: URL à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not url:
            return True, ""  # URLs vides sont acceptées
        
        if not isinstance(url, str):
            return False, "URL doit être une chaîne de caractères"
        
        # Vérifier le pattern https://www.
        if not self.WWW_PATTERN.match(url):
            return False, f"URL non conforme (doit être https://www.*): {url}"
        
        return True, ""
    
    def _validate_document_urls(self, document: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide toutes les URLs d'un document.
        
        Args:
            document: Document à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        for url_field in self.URL_FIELDS:
            if url_field in document and document[url_field]:
                is_valid, error = self._validate_url_format(document[url_field])
                if not is_valid:
                    errors.append(f"{url_field}: {error}")
                else:
                    self._stats['urls_validated'] += 1
        
        if errors:
            self._stats['urls_rejected'] += len(errors)
        
        return len(errors) == 0, errors
    
    def _normalize_document_urls(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise toutes les URLs d'un document.
        
        Args:
            document: Document à normaliser
            
        Returns:
            Document avec URLs normalisées
        """
        normalized = document.copy()
        
        for url_field in self.URL_FIELDS:
            if url_field in normalized and normalized[url_field]:
                result = seo_normalizer.normalize_url(normalized[url_field])
                if result.normalized_url and not result.url_invalid:
                    normalized[url_field] = result.normalized_url
        
        # Ajouter le flag de normalisation
        normalized['url_normalized'] = True
        normalized['normalized_at'] = datetime.now(timezone.utc).isoformat()
        
        return normalized
    
    async def insert(
        self,
        collection_name: str,
        document: Dict[str, Any],
        auto_normalize: bool = True,
        strict_validation: bool = True
    ) -> InsertionResult:
        """
        Insère un document dans la collection après validation des URLs.
        
        RÈGLE COPILOT MAÎTRE:
        - Vérifier que toutes les URLs respectent le format https://www.[domaine]
        - Rejeter toute entrée non conforme
        - Ajouter flag url_normalized = true
        
        Args:
            collection_name: Nom de la collection
            document: Document à insérer
            auto_normalize: Normaliser automatiquement les URLs avant validation
            strict_validation: Rejeter les documents avec URLs non conformes
            
        Returns:
            InsertionResult avec détails de l'opération
        """
        await self.connect()
        
        result = InsertionResult(original_document=document.copy())
        
        # Étape 1: Normaliser si demandé
        if auto_normalize:
            document = self._normalize_document_urls(document)
            result.url_normalized = True
        
        result.normalized_document = document.copy()
        
        # Étape 2: Valider les URLs
        if strict_validation:
            is_valid, errors = self._validate_document_urls(document)
            
            if not is_valid:
                result.success = False
                result.rejected = True
                result.rejection_reason = "; ".join(errors)
                self._stats['total_rejections'] += 1
                return result
        
        # Étape 3: Ajouter métadonnées
        document['created_at'] = datetime.now(timezone.utc).isoformat()
        document['updated_at'] = document['created_at']
        
        # Étape 4: Insérer en base
        try:
            collection = self._db[collection_name]
            insert_result = await collection.insert_one(document)
            
            result.success = True
            result.document_id = str(insert_result.inserted_id)
            self._stats['total_insertions'] += 1
            
        except DuplicateKeyError as e:
            result.success = False
            result.rejected = True
            result.rejection_reason = f"Document dupliqué: {str(e)}"
            self._stats['total_duplicates'] += 1
            
        except PyMongoError as e:
            result.success = False
            result.rejected = True
            result.rejection_reason = f"Erreur MongoDB: {str(e)}"
            self._stats['total_rejections'] += 1
        
        return result
    
    async def insert_batch(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        auto_normalize: bool = True,
        strict_validation: bool = True,
        skip_duplicates: bool = True
    ) -> BatchInsertionResult:
        """
        Insère un lot de documents après validation.
        
        Args:
            collection_name: Nom de la collection
            documents: Liste des documents à insérer
            auto_normalize: Normaliser automatiquement les URLs
            strict_validation: Rejeter les documents non conformes
            skip_duplicates: Ignorer les duplicats au lieu de stopper
            
        Returns:
            BatchInsertionResult avec statistiques
        """
        await self.connect()
        
        batch_result = BatchInsertionResult(total_processed=len(documents))
        
        valid_documents = []
        
        for doc in documents:
            # Normaliser
            if auto_normalize:
                doc = self._normalize_document_urls(doc)
            
            # Valider
            if strict_validation:
                is_valid, errors = self._validate_document_urls(doc)
                
                if not is_valid:
                    batch_result.total_rejected += 1
                    batch_result.rejected_documents.append({
                        'document': doc,
                        'errors': errors
                    })
                    continue
            
            # Ajouter métadonnées
            doc['created_at'] = datetime.now(timezone.utc).isoformat()
            doc['updated_at'] = doc['created_at']
            
            valid_documents.append(doc)
        
        # Insérer les documents valides
        if valid_documents:
            try:
                collection = self._db[collection_name]
                
                if skip_duplicates:
                    # Insérer un par un pour gérer les duplicats
                    for doc in valid_documents:
                        try:
                            insert_result = await collection.insert_one(doc)
                            batch_result.total_inserted += 1
                            batch_result.inserted_ids.append(str(insert_result.inserted_id))
                            self._stats['total_insertions'] += 1
                        except DuplicateKeyError:
                            batch_result.total_duplicates += 1
                            batch_result.duplicate_documents.append(doc)
                            self._stats['total_duplicates'] += 1
                else:
                    # Insertion en masse
                    insert_result = await collection.insert_many(valid_documents, ordered=False)
                    batch_result.total_inserted = len(insert_result.inserted_ids)
                    batch_result.inserted_ids = [str(id) for id in insert_result.inserted_ids]
                    self._stats['total_insertions'] += batch_result.total_inserted
                    
            except PyMongoError:
                # En cas d'erreur, certains documents peuvent avoir été insérés
                pass
        
        return batch_result
    
    async def update_with_validation(
        self,
        collection_name: str,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any],
        auto_normalize: bool = True,
        strict_validation: bool = True
    ) -> InsertionResult:
        """
        Met à jour un document après validation des nouvelles URLs.
        
        Args:
            collection_name: Nom de la collection
            filter_query: Filtre de sélection du document
            update_data: Données de mise à jour
            auto_normalize: Normaliser automatiquement les URLs
            strict_validation: Rejeter si URLs non conformes
            
        Returns:
            InsertionResult avec détails de l'opération
        """
        await self.connect()
        
        result = InsertionResult(original_document=update_data.copy())
        
        # Normaliser si demandé
        if auto_normalize:
            update_data = self._normalize_document_urls(update_data)
            result.url_normalized = True
        
        result.normalized_document = update_data.copy()
        
        # Valider
        if strict_validation:
            is_valid, errors = self._validate_document_urls(update_data)
            
            if not is_valid:
                result.success = False
                result.rejected = True
                result.rejection_reason = "; ".join(errors)
                self._stats['total_rejections'] += 1
                return result
        
        # Mettre à jour
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        try:
            collection = self._db[collection_name]
            update_result = await collection.update_one(
                filter_query,
                {'$set': update_data}
            )
            
            if update_result.modified_count > 0:
                result.success = True
            else:
                result.success = False
                result.rejection_reason = "Aucun document trouvé ou modifié"
                
        except PyMongoError as e:
            result.success = False
            result.rejected = True
            result.rejection_reason = f"Erreur MongoDB: {str(e)}"
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la base de données"""
        return self._stats.copy()
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        for key in self._stats:
            self._stats[key] = 0


# Instance globale du module
seo_db = SEODatabase()


async def insert(
    collection_name: str,
    document: Dict[str, Any],
    auto_normalize: bool = True,
    strict_validation: bool = True
) -> InsertionResult:
    """
    Fonction utilitaire pour insérer un document.
    Point d'entrée principal conforme à la directive COPILOT MAÎTRE.
    """
    return await seo_db.insert(collection_name, document, auto_normalize, strict_validation)


async def insert_batch(
    collection_name: str,
    documents: List[Dict[str, Any]],
    auto_normalize: bool = True,
    strict_validation: bool = True
) -> BatchInsertionResult:
    """
    Fonction utilitaire pour insérer un lot de documents.
    """
    return await seo_db.insert_batch(collection_name, documents, auto_normalize, strict_validation)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE VERROUILLÉ — v1.0.0
# Toute modification requiert approbation COPILOT MAÎTRE
# ══════════════════════════════════════════════════════════════════════════════

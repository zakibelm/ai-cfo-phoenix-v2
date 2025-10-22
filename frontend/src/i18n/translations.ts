/**
 * Translations for the application
 * Supports French (fr) and English (en)
 */

export type Language = 'fr' | 'en';

export interface Translations {
  [key: string]: string;
}

export const translations: Record<Language, Translations> = {
  fr: {
    // Common
    app_name: 'AI CFO Suite - Phoenix',
    welcome: 'Bienvenue',
    error: 'Erreur',
    success: 'Succès',
    loading: 'Chargement...',
    save: 'Enregistrer',
    cancel: 'Annuler',
    delete: 'Supprimer',
    edit: 'Modifier',
    create: 'Créer',
    search: 'Rechercher',
    filter: 'Filtrer',
    export: 'Exporter',
    import: 'Importer',
    
    // Navigation
    dashboard: 'Tableau de bord',
    upload: 'Téléverser',
    explore: 'Explorer',
    playground: 'Playground',
    monitoring: 'Monitoring',
    admin: 'Administration',
    agents: 'Agents',
    settings: 'Paramètres',
    
    // Documents
    documents: 'Documents',
    document: 'Document',
    upload_document: 'Téléverser un document',
    document_uploaded: 'Document téléversé avec succès',
    document_deleted: 'Document supprimé',
    no_documents: 'Aucun document',
    document_name: 'Nom du document',
    document_type: 'Type de document',
    document_size: 'Taille',
    upload_date: 'Date de téléversement',
    drag_drop: 'Glissez-déposez vos fichiers ici',
    or_click: 'ou cliquez pour sélectionner',
    
    // Agents
    agent_name: 'Nom de l\'agent',
    agent_role: 'Rôle',
    agent_goal: 'Objectif',
    agent_backstory: 'Contexte',
    system_prompt: 'Prompt système',
    agent_created: 'Agent créé avec succès',
    agent_updated: 'Agent mis à jour',
    agent_deleted: 'Agent supprimé',
    no_agents: 'Aucun agent',
    create_agent: 'Créer un agent',
    edit_agent: 'Modifier l\'agent',
    delete_agent: 'Supprimer l\'agent',
    agent_active: 'Actif',
    agent_inactive: 'Inactif',
    local_agent: 'Agent local',
    remote_agent: 'Agent distant (SSH)',
    test_connection: 'Tester la connexion',
    connection_successful: 'Connexion réussie',
    connection_failed: 'Échec de la connexion',
    reload_agents: 'Recharger les agents',
    
    // SSH
    ssh_host: 'Hôte SSH',
    ssh_port: 'Port SSH',
    ssh_username: 'Nom d\'utilisateur',
    ssh_password: 'Mot de passe',
    ssh_key_path: 'Chemin de la clé SSH',
    ssh_endpoint: 'Point de terminaison',
    
    // Queries
    query: 'Requête',
    ask_question: 'Poser une question',
    response: 'Réponse',
    sources: 'Sources',
    no_response: 'Aucune réponse',
    processing: 'Traitement en cours...',
    query_sent: 'Requête envoyée',
    query_failed: 'Échec de la requête',
    send: 'Envoyer',
    clear: 'Effacer',
    
    // Monitoring
    health_status: 'État de santé',
    healthy: 'Sain',
    degraded: 'Dégradé',
    unhealthy: 'Non sain',
    uptime: 'Temps de fonctionnement',
    total_requests: 'Total des requêtes',
    error_rate: 'Taux d\'erreur',
    response_time: 'Temps de réponse',
    success_rate: 'Taux de succès',
    last_request: 'Dernière requête',
    metrics: 'Métriques',
    refresh: 'Actualiser',
    auto_refresh: 'Actualisation automatique',
    system_metrics: 'Métriques système',
    agent_metrics: 'Métriques des agents',
    ssh_connections: 'Connexions SSH',
    
    // Errors
    error_occurred: 'Une erreur s\'est produite',
    invalid_input: 'Entrée invalide',
    required_field: 'Champ requis',
    file_too_large: 'Fichier trop volumineux',
    unsupported_format: 'Format non supporté',
    network_error: 'Erreur réseau',
    server_error: 'Erreur serveur',
    not_found: 'Non trouvé',
    unauthorized: 'Non autorisé',
    forbidden: 'Interdit',
    
    // Agent roles
    accountant: 'Expert Comptable',
    tax_expert: 'Expert Fiscal',
    forecast_analyst: 'Analyste Prévisionnel',
    compliance_expert: 'Expert Conformité',
    auditor: 'Auditeur',
    reporter: 'Générateur de Rapports',
    
    // Jurisdictions
    jurisdiction: 'Juridiction',
    country: 'Pays',
    province: 'Province',
    canada: 'Canada',
    quebec: 'Québec',
    ontario: 'Ontario',
    france: 'France',
    usa: 'États-Unis',
    
    // Models
    model: 'Modèle',
    select_model: 'Sélectionner un modèle',
    model_provider: 'Fournisseur',
    model_cost: 'Coût',
    tokens_used: 'Tokens utilisés',
    estimated_cost: 'Coût estimé',
    available_models: 'Modèles disponibles',
    
    // Language
    language: 'Langue',
    french: 'Français',
    english: 'English',
  },
  
  en: {
    // Common
    app_name: 'AI CFO Suite - Phoenix',
    welcome: 'Welcome',
    error: 'Error',
    success: 'Success',
    loading: 'Loading...',
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    search: 'Search',
    filter: 'Filter',
    export: 'Export',
    import: 'Import',
    
    // Navigation
    dashboard: 'Dashboard',
    upload: 'Upload',
    explore: 'Explore',
    playground: 'Playground',
    monitoring: 'Monitoring',
    admin: 'Administration',
    agents: 'Agents',
    settings: 'Settings',
    
    // Documents
    documents: 'Documents',
    document: 'Document',
    upload_document: 'Upload document',
    document_uploaded: 'Document uploaded successfully',
    document_deleted: 'Document deleted',
    no_documents: 'No documents',
    document_name: 'Document name',
    document_type: 'Document type',
    document_size: 'Size',
    upload_date: 'Upload date',
    drag_drop: 'Drag and drop your files here',
    or_click: 'or click to select',
    
    // Agents
    agent_name: 'Agent name',
    agent_role: 'Role',
    agent_goal: 'Goal',
    agent_backstory: 'Backstory',
    system_prompt: 'System prompt',
    agent_created: 'Agent created successfully',
    agent_updated: 'Agent updated',
    agent_deleted: 'Agent deleted',
    no_agents: 'No agents',
    create_agent: 'Create agent',
    edit_agent: 'Edit agent',
    delete_agent: 'Delete agent',
    agent_active: 'Active',
    agent_inactive: 'Inactive',
    local_agent: 'Local agent',
    remote_agent: 'Remote agent (SSH)',
    test_connection: 'Test connection',
    connection_successful: 'Connection successful',
    connection_failed: 'Connection failed',
    reload_agents: 'Reload agents',
    
    // SSH
    ssh_host: 'SSH host',
    ssh_port: 'SSH port',
    ssh_username: 'Username',
    ssh_password: 'Password',
    ssh_key_path: 'SSH key path',
    ssh_endpoint: 'Endpoint',
    
    // Queries
    query: 'Query',
    ask_question: 'Ask a question',
    response: 'Response',
    sources: 'Sources',
    no_response: 'No response',
    processing: 'Processing...',
    query_sent: 'Query sent',
    query_failed: 'Query failed',
    send: 'Send',
    clear: 'Clear',
    
    // Monitoring
    health_status: 'Health status',
    healthy: 'Healthy',
    degraded: 'Degraded',
    unhealthy: 'Unhealthy',
    uptime: 'Uptime',
    total_requests: 'Total requests',
    error_rate: 'Error rate',
    response_time: 'Response time',
    success_rate: 'Success rate',
    last_request: 'Last request',
    metrics: 'Metrics',
    refresh: 'Refresh',
    auto_refresh: 'Auto-refresh',
    system_metrics: 'System metrics',
    agent_metrics: 'Agent metrics',
    ssh_connections: 'SSH connections',
    
    // Errors
    error_occurred: 'An error occurred',
    invalid_input: 'Invalid input',
    required_field: 'Required field',
    file_too_large: 'File too large',
    unsupported_format: 'Unsupported format',
    network_error: 'Network error',
    server_error: 'Server error',
    not_found: 'Not found',
    unauthorized: 'Unauthorized',
    forbidden: 'Forbidden',
    
    // Agent roles
    accountant: 'Accountant',
    tax_expert: 'Tax Expert',
    forecast_analyst: 'Forecast Analyst',
    compliance_expert: 'Compliance Expert',
    auditor: 'Auditor',
    reporter: 'Report Generator',
    
    // Jurisdictions
    jurisdiction: 'Jurisdiction',
    country: 'Country',
    province: 'Province',
    canada: 'Canada',
    quebec: 'Quebec',
    ontario: 'Ontario',
    france: 'France',
    usa: 'United States',
    
    // Models
    model: 'Model',
    select_model: 'Select model',
    model_provider: 'Provider',
    model_cost: 'Cost',
    tokens_used: 'Tokens used',
    estimated_cost: 'Estimated cost',
    available_models: 'Available models',
    
    // Language
    language: 'Language',
    french: 'Français',
    english: 'English',
  }
};

export const getTranslation = (key: string, language: Language): string => {
  return translations[language][key] || key;
};

export const getSupportedLanguages = (): Language[] => {
  return ['fr', 'en'];
};

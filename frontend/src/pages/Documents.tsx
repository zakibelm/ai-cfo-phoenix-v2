import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiDownload, FiTrash2, FiFileText, FiRefreshCw, FiUpload, FiX } from 'react-icons/fi';
import { useDocuments, useDeleteDocument, useDownloadDocument } from '../hooks/useDocuments';
import { uploadDocuments } from '../services/apiService';
import { Document } from '../App';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

interface DocumentsProps {
  documents: Document[];
  setDocuments: React.Dispatch<React.SetStateAction<Document[]>>;
  addDocument: (doc: Document) => void;
}

const AVAILABLE_AGENTS = [
  'AccountantAgent',
  'TaxAgent',
  'ForecastAgent',
  'ComplianceAgent',
  'AuditAgent',
  'ReporterAgent'
];

const DocumentsPage: React.FC<DocumentsProps> = ({ addDocument }) => {
  const { data: documents = [], isLoading, refetch } = useDocuments('documents');
  const deleteMutation = useDeleteDocument();
  const downloadMutation = useDownloadDocument();
  
  const [files, setFiles] = useState<File[]>([]);
  const [assignedAgents, setAssignedAgents] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showUploadSection, setShowUploadSection] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files));
    }
  };

  const onDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files) {
      setFiles(Array.from(event.dataTransfer.files));
    }
  }, []);

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleAgentToggle = (agent: string) => {
    setAssignedAgents(prev =>
      prev.includes(agent)
        ? prev.filter(a => a !== agent)
        : [...prev, agent]
    );
  };

  const handleUpload = async () => {
    if (files.length === 0 || isUploading) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 300);

      const response = await uploadDocuments(files, {
        agents: assignedAgents,
        doctype: 'Financial Document',
        country: 'CA'
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const newDoc: Document = {
        id: response.document_id,
        name: response.filename,
        status: 'Processed',
        uploaded: new Date().toISOString().split('T')[0],
        assigned_agents: assignedAgents,
        tags: ['New', 'Upload'],
        doctype: 'Financial Document',
        country: 'CA'
      };
      addDocument(newDoc);

      toast.success('Document téléversé avec succès');

      setTimeout(() => {
        setFiles([]);
        setAssignedAgents([]);
        setUploadProgress(0);
        setIsUploading(false);
        setShowUploadSection(false);
        refetch();
      }, 1000);

    } catch (err: any) {
      toast.error(err.message || 'Échec du téléversement');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDelete = (docId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      deleteMutation.mutate({ collectionName: 'documents', documentId: docId });
    }
  };

  const handleDownload = (docId: string, filename: string) => {
    downloadMutation.mutate({ collectionName: 'documents', documentId: docId, filename });
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl md:text-4xl font-bold mb-2 text-gradient-primary">
          Gestion des Documents
        </h1>
        <p className="text-secondary-text">
          Téléversez de nouveaux documents ou gérez ceux existants dans le RAG.
        </p>
      </motion.div>

      {/* Upload Toggle Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mb-6"
      >
        <Button
          variant="primary"
          icon={showUploadSection ? <FiX /> : <FiUpload />}
          onClick={() => setShowUploadSection(!showUploadSection)}
        >
          {showUploadSection ? 'Fermer' : 'Téléverser un document'}
        </Button>
      </motion.div>

      {/* Upload Section */}
      <AnimatePresence>
        {showUploadSection && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-12 overflow-hidden"
          >
            <Card className="p-6">
              {files.length === 0 ? (
                <div
                  className="border-2 border-dashed border-border-color rounded-lg p-12 text-center hover:border-primary-accent/50 transition-all cursor-pointer"
                  onDrop={onDrop}
                  onDragOver={onDragOver}
                >
                  <input
                    type="file"
                    id="file-upload"
                    multiple
                    accept=".pdf,.docx,.txt,.csv"
                    className="hidden"
                    onChange={handleFileChange}
                    disabled={isUploading}
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <FiUpload className="text-6xl mx-auto mb-4 text-primary-accent" />
                    <p className="text-xl text-primary-text mb-2">
                      <span className="text-primary-accent hover:underline">
                        Cliquez pour parcourir
                      </span>{' '}
                      ou glissez-déposez vos fichiers
                    </p>
                    <p className="text-secondary-text">
                      Formats supportés : PDF, DOCX, TXT, CSV
                    </p>
                  </label>
                </div>
              ) : (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-semibold">
                      Configuration d'Ingestion
                    </h2>
                    <Button
                      variant="ghost"
                      onClick={() => setFiles([])}
                      disabled={isUploading}
                    >
                      Effacer la sélection
                    </Button>
                  </div>

                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-3">
                      Fichiers Sélectionnés ({files.length})
                    </h3>
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-center justify-between p-3 bg-background rounded-lg"
                        >
                          <span className="text-primary-text flex items-center gap-2">
                            <FiFileText className="text-primary-accent" />
                            {file.name}
                          </span>
                          <span className="text-secondary-text text-sm">
                            {(file.size / 1024).toFixed(2)} KB
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-3">
                      Assigner aux Agents
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {AVAILABLE_AGENTS.map((agent, index) => (
                        <motion.button
                          key={agent}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          onClick={() => handleAgentToggle(agent)}
                          disabled={isUploading}
                          className={`p-3 rounded-lg border transition-all ${
                            assignedAgents.includes(agent)
                              ? 'bg-primary-accent/20 border-primary-accent text-primary-accent'
                              : 'bg-background border-border-color text-secondary-text hover:border-primary-accent/50'
                          }`}
                        >
                          {agent}
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  <Button
                    variant="primary"
                    fullWidth
                    onClick={handleUpload}
                    disabled={isUploading || files.length === 0}
                    loading={isUploading}
                  >
                    {isUploading
                      ? `Upload en cours... ${uploadProgress}%`
                      : `Démarrer l'Ingestion (${files.length} fichier${files.length > 1 ? 's' : ''})`}
                  </Button>

                  {isUploading && (
                    <div className="mt-4 bg-background rounded-full h-2 overflow-hidden">
                      <motion.div
                        className="bg-primary-accent h-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${uploadProgress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  )}
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Documents List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl md:text-3xl font-semibold">Documents dans le RAG</h2>
          <Button
            variant="ghost"
            onClick={() => refetch()}
            disabled={isLoading}
            icon={<FiRefreshCw className={isLoading ? 'animate-spin' : ''} />}
          >
            Actualiser
          </Button>
        </div>

        {isLoading ? (
          <Card className="p-12">
            <LoadingSpinner size="lg" />
            <p className="text-center text-secondary-text mt-4">Chargement des documents...</p>
          </Card>
        ) : documents.length > 0 ? (
          <div className="grid gap-4">
            {documents.map((doc: any, index: number) => (
              <motion.div
                key={doc.document_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card hover className="p-4 md:p-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <FiFileText className="text-2xl text-primary-accent flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <h3 className="font-medium text-primary-text truncate">
                          {doc.filename}
                        </h3>
                        <p className="text-sm text-secondary-text">
                          {doc.created_at ? format(new Date(doc.created_at), 'dd/MM/yyyy HH:mm') : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(doc.document_id, doc.filename)}
                        icon={<FiDownload />}
                        disabled={downloadMutation.isPending}
                      >
                        <span className="hidden md:inline">Télécharger</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(doc.document_id)}
                        icon={<FiTrash2 />}
                        disabled={deleteMutation.isPending}
                        className="text-red-500 hover:text-red-600"
                      >
                        <span className="hidden md:inline">Supprimer</span>
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <FiFileText className="text-6xl text-secondary-text mx-auto mb-4" />
            <p className="text-secondary-text">Aucun document trouvé dans le RAG.</p>
          </Card>
        )}
      </motion.div>
    </div>
  );
};

export default DocumentsPage;


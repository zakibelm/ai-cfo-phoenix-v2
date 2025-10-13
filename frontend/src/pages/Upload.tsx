import React, { useState, useCallback } from 'react';
import { Document } from '../App';
import { uploadDocuments } from '../services/apiService';

interface UploadProps {
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

const Upload: React.FC<UploadProps> = ({ addDocument }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [assignedAgents, setAssignedAgents] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files));
      setError(null);
    }
  };

  const onDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files) {
      setFiles(Array.from(event.dataTransfer.files));
      setError(null);
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
    setError(null);
    setUploadProgress(0);

    try {
      // Simulate progress
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

      // Add document to list
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

      // Reset form
      setTimeout(() => {
        setFiles([]);
        setAssignedAgents([]);
        setUploadProgress(0);
        setIsUploading(false);
      }, 1000);

    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-4xl font-heading font-bold mb-2">
        Pipeline d'Ingestion RAG
      </h1>
      <p className="text-secondary-text mb-8">
        Uploadez vos documents financiers pour les vectoriser et les rendre accessibles aux agents
      </p>

      {error && (
        <div className="mb-6 p-4 bg-red/20 border border-red rounded-lg text-red">
          {error}
        </div>
      )}

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
            <div className="text-6xl mb-4">📤</div>
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
        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-heading font-semibold">
              Configuration d'Ingestion
            </h2>
            <button
              onClick={() => setFiles([])}
              disabled={isUploading}
              className="text-secondary-text hover:text-primary-accent transition-colors"
            >
              Effacer la sélection
            </button>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">
              Fichiers Sélectionnés ({files.length})
            </h3>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-background rounded-lg"
                >
                  <span className="text-primary-text">{file.name}</span>
                  <span className="text-secondary-text text-sm">
                    {(file.size / 1024).toFixed(2)} KB
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">
              Assigner aux Agents
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {AVAILABLE_AGENTS.map(agent => (
                <button
                  key={agent}
                  onClick={() => handleAgentToggle(agent)}
                  disabled={isUploading}
                  className={`p-3 rounded-lg border transition-all ${
                    assignedAgents.includes(agent)
                      ? 'bg-primary-accent/20 border-primary-accent text-primary-accent'
                      : 'bg-background border-border-color text-secondary-text hover:border-primary-accent/50'
                  }`}
                >
                  {agent}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={isUploading || files.length === 0}
            className="w-full bg-primary-accent text-background font-semibold py-3 rounded-lg hover:bg-primary-accent/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading
              ? `Upload en cours... ${uploadProgress}%`
              : `Démarrer l'Ingestion (${files.length} fichier${files.length > 1 ? 's' : ''})`}
          </button>

          {isUploading && (
            <div className="mt-4 bg-background rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary-accent h-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Upload;

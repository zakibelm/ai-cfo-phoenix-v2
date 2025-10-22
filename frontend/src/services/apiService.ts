import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface QueryResponse {
  agent: string;
  response: string;
  sources: Array<{
    text: string;
    score: number;
    metadata: Record<string, any>;
  }>;
  tool_calls: Array<{
    tool_name: string;
    input: Record<string, any>;
  }>;
  processing_time: number;
}

export interface UploadResponse {
  message: string;
  document_id: string;
  filename: string;
  status: string;
  processing_time?: number;
}

export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

export const sendQuery = async (
  query: string,
  ragContext: any | null,
  signal?: AbortSignal
): Promise<QueryResponse> => {
  const payload = {
    query,
    document_name: ragContext ? ragContext.name : null,
  };

  const response = await api.post<QueryResponse>('/query', payload, { signal });
  return response.data;
};

export const uploadDocuments = async (
  files: File[],
  metadata: {
    agents: string[];
    doctype: string;
    country?: string;
    province?: string;
    year?: number;
  }
): Promise<UploadResponse> => {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });

  formData.append('assigned_agents', metadata.agents.join(','));
  formData.append('doctype', metadata.doctype);
  if (metadata.country) formData.append('country', metadata.country);
  if (metadata.province) formData.append('province', metadata.province);
  if (metadata.year) formData.append('year', metadata.year.toString());

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const fetchDocuments = async (): Promise<any[]> => {
  const response = await api.get('/documents');
  return response.data.documents || [];
};

export const fetchAgents = async (): Promise<any[]> => {
  const response = await api.get('/agents');
  return response.data.agents || [];
};

export default api;


// Function to list documents from the pre-embedded RAG
export const listDocuments = async (collectionName: string): Promise<any[]> => {
  const response = await fetch(`${API_BASE_URL}/preembedded-ingestion/documents/${collectionName}`);
  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }
  const data = await response.json();
  return data.documents;
};

// Function to delete a document from the RAG
export const deleteDocument = async (collectionName: string, documentId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/preembedded-ingestion/documents/${collectionName}/${documentId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
};

// Function to download document content
export const downloadDocument = async (collectionName: string, documentId: string, filename: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/preembedded-ingestion/documents/${collectionName}/${documentId}/download`);
  if (!response.ok) {
    throw new Error('Failed to download document');
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};


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

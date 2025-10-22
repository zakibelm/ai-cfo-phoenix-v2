import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface HistoryEntry {
  id: string;
  title: string;
  type: 'chat' | 'query' | 'analysis' | 'document';
  preview: string;
  created_at: string;
  updated_at?: string;
  is_favorite: boolean;
  tags: string[];
}

export interface HistoryCreate {
  title: string;
  type: string;
  content: any;
  tags?: string[];
}

export interface HistoryUpdate {
  title?: string;
  is_favorite?: boolean;
  tags?: string[];
}

export const useHistory = (
  limit: number = 50,
  type?: string,
  favoritesOnly: boolean = false
) => {
  return useQuery({
    queryKey: ['history', limit, type, favoritesOnly],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: limit.toString(),
        favorites_only: favoritesOnly.toString(),
      });
      
      if (type) {
        params.append('type', type);
      }
      
      const response = await axios.get<HistoryEntry[]>(
        `${API_BASE_URL}/history?${params.toString()}`
      );
      return response.data;
    },
    staleTime: 1000 * 60, // 1 minute
  });
};

export const useHistoryEntry = (entryId: string) => {
  return useQuery({
    queryKey: ['history', entryId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/history/${entryId}`);
      return response.data;
    },
    enabled: !!entryId,
  });
};

export const useCreateHistoryEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: HistoryCreate) => {
      const response = await axios.post(`${API_BASE_URL}/history`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    },
  });
};

export const useUpdateHistoryEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: HistoryUpdate }) => {
      const response = await axios.patch(`${API_BASE_URL}/history/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      toast.success('Historique mis à jour');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erreur lors de la mise à jour');
    },
  });
};

export const useDeleteHistoryEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await axios.delete(`${API_BASE_URL}/history/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      toast.success('Entrée supprimée');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    },
  });
};

export const useClearHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (type?: string) => {
      const params = type ? `?type=${type}` : '';
      const response = await axios.delete(`${API_BASE_URL}/history${params}`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      toast.success(`${data.count} entrée(s) supprimée(s)`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    },
  });
};


import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listDocuments, deleteDocument, downloadDocument } from '../services/apiService';
import toast from 'react-hot-toast';

export const useDocuments = (collectionName: string = 'documents') => {
  return useQuery({
    queryKey: ['documents', collectionName],
    queryFn: () => listDocuments(collectionName),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ collectionName, documentId }: { collectionName: string; documentId: string }) =>
      deleteDocument(collectionName, documentId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['documents', variables.collectionName] });
      toast.success('Document supprimé avec succès');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Échec de la suppression du document');
    },
  });
};

export const useDownloadDocument = () => {
  return useMutation({
    mutationFn: ({ 
      collectionName, 
      documentId, 
      filename 
    }: { 
      collectionName: string; 
      documentId: string; 
      filename: string;
    }) => downloadDocument(collectionName, documentId, filename),
    onSuccess: () => {
      toast.success('Téléchargement démarré');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Échec du téléchargement');
    },
  });
};


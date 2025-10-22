import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authService, LoginCredentials, RegisterData, User } from '../services/authService';
import { useStore } from '../store/useStore';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export const useLogin = () => {
  const { login: storeLogin } = useStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: async (data) => {
      // Fetch user data
      const user = await authService.getCurrentUser();
      
      // Update store
      storeLogin(user, data.access_token, data.refresh_token);
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      
      toast.success(`Bienvenue, ${user.full_name} !`);
      navigate('/');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Échec de la connexion');
    },
  });
};

export const useRegister = () => {
  const { login: storeLogin } = useStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: RegisterData) => authService.register(data),
    onSuccess: async (data) => {
      // Fetch user data
      const user = await authService.getCurrentUser();
      
      // Update store
      storeLogin(user, data.access_token, data.refresh_token);
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      
      toast.success('Compte créé avec succès !');
      navigate('/');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Échec de l\'inscription');
    },
  });
};

export const useLogout = () => {
  const { logout: storeLogout } = useStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      storeLogout();
      queryClient.clear();
      toast.success('Déconnexion réussie');
      navigate('/login');
    },
  });
};

export const useCurrentUser = () => {
  const { isAuthenticated } = useStore();

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authService.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
  });
};


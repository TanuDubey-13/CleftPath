import React, { createContext, useContext, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCurrentUser, loginUser, logoutUser, registerUser } from '../api/auth';
import { LoginRequest, RegisterRequest, User } from '../types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  patientCount: number;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  const [patientCount, setPatientCount] = useState<number>(0);

  // Check current session on mount / refetch
  const { data, isLoading, isError } = useQuery({
    queryKey: ['currentUser'],
    queryFn: fetchCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (data?.user) {
      setUser(data.user);
      setPatientCount(data.patient_count || 0);
    } else if (isError) {
      setUser(null);
      setPatientCount(0);
    }
  }, [data, isError]);

  const loginMutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (resData) => {
      setUser(resData.user);
      queryClient.setQueryData(['currentUser'], { user: resData.user, patient_count: 0 });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: registerUser,
    onSuccess: (resData) => {
      setUser(resData.user);
      queryClient.setQueryData(['currentUser'], { user: resData.user, patient_count: 0 });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: logoutUser,
    onSuccess: () => {
      setUser(null);
      setPatientCount(0);
      queryClient.clear();
    },
  });

  const handleLogin = async (credentials: LoginRequest) => {
    await loginMutation.mutateAsync(credentials);
  };

  const handleRegister = async (payload: RegisterRequest) => {
    await registerMutation.mutateAsync(payload);
  };

  const handleLogout = async () => {
    try {
      await logoutMutation.mutateAsync();
    } catch {
      // Clear client state even if backend logout request fails
      setUser(null);
      setPatientCount(0);
      queryClient.clear();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        patientCount,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

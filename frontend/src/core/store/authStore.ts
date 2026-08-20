import { create } from 'zustand';
import { UserProfile } from '../types/auth.types';

interface AuthState {
  user: UserProfile | null;
  selectedParishId: string | null;
  setUser: (user: UserProfile | null) => void;
  setSelectedParishId: (parishId: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  selectedParishId: null,
  setUser: (user) => set({ user }),
  setSelectedParishId: (selectedParishId) => set({ selectedParishId }),
}));

import { useMemo, useEffect, useContext } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AuthContext } from '../auth/AuthContext';
import { useAuthStore } from '../store/authStore';
import { domainApi, Parish } from '../api/domain';

const ARCHDIOCESAN_ROLES = ['SUPER_ADMIN', 'CHANCELLOR', 'ECONOMO', 'READ_ONLY_AUDITOR'];
const STORAGE_KEY = 'arkidi_selected_parish_id';

export function useActiveParish() {
  const authContext = useContext(AuthContext);
  const { user: storeUser, selectedParishId, setSelectedParishId } = useAuthStore();
  const user = authContext?.user ?? storeUser;

  const parishesQuery = useQuery({
    queryKey: ['parishes'],
    queryFn: () => domainApi.listParishes(),
  });

  const parishes = parishesQuery.data || [];

  const canChangeParish = useMemo(() => {
    if (!user) return true;
    if (ARCHDIOCESAN_ROLES.includes(user.role)) return true;
    return !user.parish_id;
  }, [user]);

  // Determine active parish id
  const activeParishId = useMemo(() => {
    if (parishes.length === 0) {
      return null;
    }
    if (user?.parish_id && !ARCHDIOCESAN_ROLES.includes(user.role)) {
      return parishes.some((p) => p.id === user.parish_id) ? user.parish_id : parishes[0]?.id || null;
    }
    if (selectedParishId && parishes.some((p) => p.id === selectedParishId)) {
      return selectedParishId;
    }
    const saved = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
    if (saved && parishes.some((p) => p.id === saved)) {
      return saved;
    }
    return parishes[0]?.id || null;
  }, [user, selectedParishId, parishes]);

  // Keep store in sync when activeParishId is derived
  useEffect(() => {
    if (activeParishId && selectedParishId !== activeParishId) {
      setSelectedParishId(activeParishId);
    }
  }, [activeParishId, selectedParishId, setSelectedParishId]);

  const activeParish: Parish | undefined = useMemo(() => {
    return parishes.find((p) => p.id === activeParishId);
  }, [parishes, activeParishId]);

  const changeActiveParish = (parishId: string) => {
    if (!canChangeParish) return;
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, parishId);
    }
    setSelectedParishId(parishId);
  };

  return {
    parishes,
    activeParishId,
    activeParish,
    canChangeParish,
    changeActiveParish,
    isLoading: parishesQuery.isLoading,
    isError: parishesQuery.isError,
  };
}

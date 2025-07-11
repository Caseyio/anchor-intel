import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  useMemo,
  ReactNode,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

type AuthContextType = {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setLoading(false);
    navigate('/login');
  };

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const decoded: { exp: number } = jwtDecode(token);
      const exp = decoded.exp * 1000;
      const now = Date.now();

      if (now >= exp) {
        console.warn('🔒 Token expired, logging out...');
        logout();
      } else {
        const timeout = setTimeout(() => {
          console.warn('🔒 Token timed out, logging out...');
          logout();
        }, exp - now);

        setLoading(false);
        return () => clearTimeout(timeout);
      }
    } catch (err) {
      console.error('❌ Invalid token format', err);
      logout();
    }
  }, [token]);

  const isAuthenticated = useMemo(() => !!token, [token]);

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, login, logout, loading }}>
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

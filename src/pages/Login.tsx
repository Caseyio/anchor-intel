// pages/Login.tsx

import { useState, FormEvent } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API from '../services/api'; // use your Axios instance

type LocationState = {
  from?: string;
};

const Login = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setError('');

  if (!username || !password) {
    setError('⚠️ Please enter both username and password');
    return;
  }

  setLoading(true);

  try {
    const res = await API.post('/users/login', {
  username,
  password
});



    const token = res.data.access_token;
    login(token);
    const redirectPath = (location.state as LocationState)?.from || '/dashboard';
    navigate(redirectPath, { replace: true });
  } catch (err) {
    console.error('Login error:', err);
    setError('❌ Invalid username or password');
    setPassword('');
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="max-w-sm mx-auto mt-10 font-mono">
      <h1 className="text-xl font-bold mb-4 text-center">🔐 Admin Login</h1>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          className="w-full border px-3 py-2 rounded"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full border px-3 py-2 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-red-600">{error}</p>}
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded"
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;

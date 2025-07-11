// src/services/api.ts
import axios, { InternalAxiosRequestConfig } from 'axios';
import { KpiSummarySchema, KpiSummary } from "@/schemas/KpiSummary";

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : '/api');

const API = axios.create({ baseURL });

API.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = sessionStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default API;

// ─────────────────────────
// 📊 KPI Summary Endpoint
// ─────────────────────────
export const fetchKpiSummary = async (
  start_date: string,
  end_date: string
): Promise<KpiSummary> => {
  const response = await API.get("/analytics/kpi-summary", {
    params: { start_date, end_date },
  });
  return KpiSummarySchema.parse(response.data);
};

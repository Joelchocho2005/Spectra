import axios from "axios";
import { AnalyzeRequest, AnalyzeResponse } from "../types/spectra";

const API_BASE_URL = "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const SpectraService = {
  async analyze(params: AnalyzeRequest): Promise<AnalyzeResponse> {
    const response = await api.post<AnalyzeResponse>("/analyze", params);
    return response.data;
  },

  async healthCheck(): Promise<boolean> {
    try {
      const resp = await api.get("/health");
      return resp.data.status === "ok";
    } catch {
      return false;
    }
  },
};

import axios from 'axios';

const baseURL = import.meta.env.VITE_APP_BASE_URL;

const apiClient = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendCoordinate = async (request) => {
  try {
    const response = await apiClient.post("/your-endpoint", request);
    return response.data;
  } catch (error) {
    console.error("Error response:", error);
    throw error;
  }
};
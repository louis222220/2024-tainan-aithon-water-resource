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
    const response = await apiClient.post("/households/area", request);
    console.log('想看一下錯誤', response);
    
    return response.data;
  } catch (error) {
    console.error("Error response:", error);
    throw error;
  }
};
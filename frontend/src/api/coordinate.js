import axios from 'axios';

const baseURL = 'http://127.0.0.1:8000';

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
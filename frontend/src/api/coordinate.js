import axios from 'axios';

const baseURL = import.meta.env.VITE_APP_BASE_URL;

const apiClient = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 獲取座標
export const getHouseholds = async (request) => {
  try {
    const response = await apiClient.post("/households/area", request); 
    return response.data;
  } catch (error) {
    console.error("Error response:", error);
    throw error;
  }
};

// 獲取人口數
export const getPopulation = async (request) => {
  try {
    const response = await apiClient.post("/population/area", request); 
    return response.data;
  } catch (error) {
    console.error("Error response:", error);
    throw error;
  }
};
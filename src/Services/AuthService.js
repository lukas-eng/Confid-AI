import api from "../api/axios";

export const login = async (data) => {
  const res = await api.post("/auth/login", data);
  return res.data;
};

export const registro = async (data) => {
  const res = await api.post("/auth/registro", data);
  return res.data;
};


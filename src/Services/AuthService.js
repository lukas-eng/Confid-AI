import api from "../api/axios";

export const login = async (data) => {
  const res = await api.post("/login", data);
  return res.data;
};

export const registro = async (data) => {
  const res = await api.post("/registro", data);
  return res.data;
};

import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  AuthMeResponseData,
  LoginRequest,
  LogoutResponseData,
  RegisterRequest,
  TokenResponseData,
} from '../types';

export const registerUser = async (
  payload: RegisterRequest
): Promise<TokenResponseData> => {
  const response = await apiClient.post<ApiResponse<TokenResponseData>>(
    '/auth/register',
    payload
  );
  return response.data.data;
};

export const loginUser = async (
  payload: LoginRequest
): Promise<TokenResponseData> => {
  const response = await apiClient.post<ApiResponse<TokenResponseData>>(
    '/auth/login',
    payload
  );
  return response.data.data;
};

export const logoutUser = async (): Promise<LogoutResponseData> => {
  const response = await apiClient.post<ApiResponse<LogoutResponseData>>(
    '/auth/logout'
  );
  return response.data.data;
};

export const fetchCurrentUser = async (): Promise<AuthMeResponseData> => {
  const response = await apiClient.get<ApiResponse<AuthMeResponseData>>(
    '/auth/me'
  );
  return response.data.data;
};

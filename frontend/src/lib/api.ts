import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000,
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const { access_token } = response.data;
              localStorage.setItem('access_token', access_token);
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/auth/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async register(email: string, password: string, name: string) {
    const response = await this.client.post('/auth/register', { email, password, name });
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return response.data;
  }

  async refreshToken(refreshToken: string) {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  async forgotPassword(email: string) {
    const response = await this.client.post('/auth/forgot-password', { email });
    return response.data;
  }

  async resetPassword(token: string, password: string) {
    const response = await this.client.post('/auth/reset-password', { token, password });
    return response.data;
  }

  async verifyEmail(token: string) {
    const response = await this.client.post('/auth/verify-email', { token });
    return response.data;
  }

  async enable2FA() {
    const response = await this.client.post('/auth/2fa/enable');
    return response.data;
  }

  async verify2FA(code: string) {
    const response = await this.client.post('/auth/2fa/verify', { code });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async getDevices() {
    const response = await this.client.get('/devices');
    return response.data;
  }

  async getDevice(id: string) {
    const response = await this.client.get(`/devices/${id}`);
    return response.data;
  }

  async pairDevice(pairCode: string) {
    const response = await this.client.post('/devices/pair', { pair_code: pairCode });
    return response.data;
  }

  async removeDevice(id: string) {
    const response = await this.client.delete(`/devices/${id}`);
    return response.data;
  }

  async renameDevice(id: string, name: string) {
    const response = await this.client.patch(`/devices/${id}`, { name });
    return response.data;
  }

  async getDeviceGroups() {
    const response = await this.client.get('/device-groups');
    return response.data;
  }

  async createDeviceGroup(name: string, type: string) {
    const response = await this.client.post('/device-groups', { name, type });
    return response.data;
  }

  async getTasks(deviceId?: string) {
    const params = deviceId ? { device_id: deviceId } : {};
    const response = await this.client.get('/tasks', { params });
    return response.data;
  }

  async getTask(id: string) {
    const response = await this.client.get(`/tasks/${id}`);
    return response.data;
  }

  async cancelTask(id: string) {
    const response = await this.client.post(`/tasks/${id}/cancel`);
    return response.data;
  }

  async retryTask(id: string) {
    const response = await this.client.post(`/tasks/${id}/retry`);
    return response.data;
  }

  async chat(deviceId: string, message: string) {
    const response = await this.client.post('/ai/chat', { device_id: deviceId, message });
    return response.data;
  }

  async getFiles(deviceId: string, path: string) {
    const response = await this.client.get(`/files/${deviceId}`, { params: { path } });
    return response.data;
  }

  async deleteFile(deviceId: string, path: string) {
    const response = await this.client.delete(`/files/${deviceId}`, { data: { path } });
    return response.data;
  }

  async getNotifications() {
    const response = await this.client.get('/notifications');
    return response.data;
  }

  async markNotificationRead(id: string) {
    const response = await this.client.patch(`/notifications/${id}/read`);
    return response.data;
  }

  async getSubscription() {
    const response = await this.client.get('/billing/subscription');
    return response.data;
  }

  async createCheckoutSession(plan: string) {
    const response = await this.client.post('/billing/checkout', { plan });
    return response.data;
  }

  async getSettings() {
    const response = await this.client.get('/settings');
    return response.data;
  }

  async updateSettings(settings: Record<string, unknown>) {
    const response = await this.client.patch('/settings', settings);
    return response.data;
  }

  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiClient();
export default api;

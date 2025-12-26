import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // Auth endpoints
  async register(data: { email: string; password: string; full_name: string; academic_level: string }) {
    return this.post('/auth/register', data);
  }

  async login(data: { username: string; password: string }) {
    const response: any = await this.post('/auth/login', data);
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    return response;
  }

  async getCurrentUser() {
    return this.get('/auth/me');
  }

  // Course endpoints
  async getCourses() {
    return this.get('/courses');
  }

  async getCourse(id: string) {
    return this.get(`/courses/${id}`);
  }

  async createCourse(data: any) {
    return this.post('/courses', data);
  }

  async updateCourse(id: string, data: any) {
    return this.put(`/courses/${id}`, data);
  }

  async deleteCourse(id: string) {
    return this.delete(`/courses/${id}`);
  }

  // Topic endpoints
  async getTopics(courseId: string) {
    return this.get(`/courses/${courseId}/topics`);
  }

  async createTopic(courseId: string, data: any) {
    return this.post(`/courses/${courseId}/topics`, data);
  }

  async updateTopic(courseId: string, topicId: string, data: any) {
    return this.put(`/courses/${courseId}/topics/${topicId}`, data);
  }

  async deleteTopic(courseId: string, topicId: string) {
    return this.delete(`/courses/${courseId}/topics/${topicId}`);
  }

  // Mastery endpoints
  async updateMastery(data: any) {
    return this.post('/mastery/update', data);
  }

  async getCourseMastery(courseId: string) {
    return this.get(`/mastery/course/${courseId}`);
  }

  async getTopicMastery(topicId: string) {
    return this.get(`/mastery/topic/${topicId}`);
  }

  async getMasteryOverview() {
    return this.get('/mastery/overview');
  }

  // Schedule endpoints
  async generateSchedule(data: any) {
    return this.post('/schedule/generate', data);
  }

  async replanSchedule() {
    return this.post('/schedule/replan');
  }

  async getUpcomingTasks() {
    return this.get('/schedule/upcoming');
  }

  async getTodaySchedule() {
    return this.get('/schedule/today');
  }

  async updateTaskStatus(taskId: string, status: string) {
    return this.put(`/schedule/task/${taskId}/status`, { status });
  }
}

export const apiClient = new ApiClient();

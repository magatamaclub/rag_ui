import { authenticatedRequest } from './auth';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  role?: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  role?: string;
  is_active?: boolean;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  size: number;
}

// 获取用户列表
export async function getUserList(page: number = 1, size: number = 20): Promise<UserListResponse> {
  return await authenticatedRequest(`/api/v1/users?page=${page}&size=${size}`, {
    method: 'GET',
  });
}

// 获取用户详情
export async function getUserDetail(userId: number): Promise<User> {
  return await authenticatedRequest(`/api/v1/users/${userId}`, {
    method: 'GET',
  });
}

// 创建用户
export async function createUser(userData: UserCreate): Promise<User> {
  return await authenticatedRequest('/api/v1/users', {
    method: 'POST',
    data: userData,
  });
}

// 更新用户
export async function updateUser(userId: number, userData: UserUpdate): Promise<User> {
  return await authenticatedRequest(`/api/v1/users/${userId}`, {
    method: 'PUT',
    data: userData,
  });
}

// 删除用户
export async function deleteUser(userId: number): Promise<{ message: string }> {
  return await authenticatedRequest(`/api/v1/users/${userId}`, {
    method: 'DELETE',
  });
}

import { request } from './request';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * 获取存储的访问令牌
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * 获取令牌类型
 */
export const getTokenType = (): string => {
  return localStorage.getItem('token_type') || 'bearer';
};

/**
 * 检查用户是否已登录
 */
export const isAuthenticated = (): boolean => {
  const token = getAccessToken();
  return !!token;
};

/**
 * 获取认证头部
 */
export const getAuthHeader = (): Record<string, string> => {
  const token = getAccessToken();
  const tokenType = getTokenType();
  
  if (token) {
    return {
      'Authorization': `${tokenType} ${token}`,
    };
  }
  
  return {};
};

/**
 * 登出用户
 */
export const logout = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_type');
  localStorage.removeItem('user_info');
  
  // 跳转到登录页
  window.location.href = '/login';
};

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async (): Promise<User | null> => {
  try {
    const token = getAccessToken();
    if (!token) {
      return null;
    }

    const response = await request('/api/v1/auth/me', {
      method: 'GET',
      headers: getAuthHeader(),
    });

    // 缓存用户信息
    localStorage.setItem('user_info', JSON.stringify(response));
    return response;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    // 如果token无效，清除本地存储
    logout();
    return null;
  }
};

/**
 * 获取缓存的用户信息
 */
export const getCachedUser = (): User | null => {
  try {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  } catch {
    return null;
  }
};

/**
 * 带认证的请求函数
 */
export const authenticatedRequest = async (
  url: string,
  options: any = {}
): Promise<any> => {
  const authHeader = getAuthHeader();
  
  return request(url, {
    ...options,
    headers: {
      ...authHeader,
      ...options.headers,
    },
  });
};

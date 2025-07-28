// 简单的 request 工具函数
interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  headers?: Record<string, string>;
}

// 获取API基础URL
const getApiBaseUrl = () => {
  // 开发环境优先使用相对路径（通过代理）
  if (process.env.NODE_ENV === 'development') {
    return '';  // 相对路径，会被代理转发
  }
  // 生产环境使用环境变量
  return process.env.REACT_APP_API_BASE_URL || '';
};

export async function request(url: string, options: RequestOptions = {}) {
  const { method = 'GET', data, headers = {} } = options;
  
  // 构建完整URL
  const baseUrl = getApiBaseUrl();
  let fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
  
  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (data) {
    if (method === 'GET') {
      // GET 请求将 data 转换为查询参数
      const params = new URLSearchParams(data);
      fullUrl += `?${params.toString()}`;
    } else {
      // POST, PUT, DELETE 请求将 data 放入 body
      config.body = JSON.stringify(data);
    }
  }

  // 添加 token 到请求头
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  try {
    const response = await fetch(fullUrl, config);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.detail || result.message || 'Request failed');
    }
    
    return result;
  } catch (error) {
    console.error('Request error:', error);
    throw error;
  }
}

// 简单的 request 工具函数
interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  headers?: Record<string, string>;
}

export async function request(url: string, options: RequestOptions = {}) {
  const { method = 'GET', data, headers = {} } = options;
  
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
      url += `?${params.toString()}`;
    } else {
      // POST, PUT, DELETE 请求将 data 放入 body
      config.body = JSON.stringify(data);
    }
  }

  // 添加 token 到请求头
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  try {
    const response = await fetch(url, config);
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

import React from "react";
import { history, RequestConfig } from "umi";
import DatabaseGuard from "@/components/DatabaseGuard";

// 全局请求配置
export const request: RequestConfig = {
  timeout: 60000,
  errorConfig: {
    errorHandler: (error: any) => {
      if (error.response) {
        const { status } = error.response;
        if (status === 401) {
          // 未授权，跳转到登录页面
          history.push("/login");
        }
      }
      throw error;
    },
  },
  requestInterceptors: [
    (url: string, options: any) => {
      // 添加token到请求头
      const token = localStorage.getItem("token");
      if (token) {
        return {
          url,
          options: {
            ...options,
            headers: {
              ...options.headers,
              Authorization: `Bearer ${token}`,
            },
          },
        };
      }
      return { url, options };
    },
  ],
};

// 根组件配置
export function rootContainer(container: React.ReactElement) {
  // 如果是初始化页面，不需要数据库检查
  if (window.location.pathname === "/initialize") {
    return container;
  }

  // 其他页面需要检查数据库状态
  return <DatabaseGuard>{container}</DatabaseGuard>;
}

export const dva = {
  config: {
    onError(err: any) {
      err.preventDefault();
      console.error(err.message);
    },
  },
};

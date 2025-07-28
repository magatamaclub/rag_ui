import React from "react";
import { history } from "umi";
import DatabaseGuard from "@/components/DatabaseGuard";

// 根组件配置
export function rootContainer(container: React.ReactElement) {
  // 如果是初始化页面，不需要数据库检查
  if (window.location.pathname === "/initialize") {
    return container;
  }

  // 其他页面需要检查数据库状态
  return <DatabaseGuard>{container}</DatabaseGuard>;
}

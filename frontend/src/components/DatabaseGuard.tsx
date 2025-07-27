import React, { useEffect, useState } from "react";
import { Spin } from "antd";
import { history } from "umi";
import { request } from "@/utils/request";

interface DatabaseStatus {
  is_initialized: boolean;
  has_connection: boolean;
  has_tables: boolean;
  has_admin_user: boolean;
  message: string;
}

interface Props {
  children: React.ReactNode;
}

const DatabaseGuard: React.FC<Props> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    checkDatabaseStatus();
  }, []);

  const checkDatabaseStatus = async () => {
    try {
      const response = (await request("/api/v1/database/status", {
        method: "GET",
      })) as DatabaseStatus;

      if (!response.is_initialized) {
        // 如果数据库未初始化，跳转到初始化页面
        history.push("/initialize");
        return;
      }

      setIsInitialized(true);
    } catch (error) {
      console.error("Failed to check database status:", error);
      // 如果检查失败，也跳转到初始化页面
      history.push("/initialize");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Spin size="large" tip="检查数据库状态..." />
      </div>
    );
  }

  if (!isInitialized) {
    return null; // 正在跳转到初始化页面
  }

  return <>{children}</>;
};

export default DatabaseGuard;

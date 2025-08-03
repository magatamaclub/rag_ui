import React, { useState, useEffect } from "react";
import { Spin, message } from "antd";
import { history } from "umi";
import { getCurrentUser, User } from "../utils/auth";

interface AuthGuardProps {
  children: React.ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        setLoading(true);

        // 检查是否有token
        const token = localStorage.getItem("access_token");
        if (!token) {
          message.warning("请先登录");
          history.push("/login");
          return;
        }

        // 验证token有效性
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error("Authentication check failed:", error);
        message.error("登录已过期，请重新登录");
        // 清除无效token
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");
        history.push("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
        }}
      >
        <Spin size="large" />
        <div style={{ marginTop: 16, color: "#666" }}>正在验证登录状态...</div>
      </div>
    );
  }

  if (!user) {
    return null; // 用户未登录，已重定向到登录页
  }

  return <>{children}</>;
};

export default AuthGuard;

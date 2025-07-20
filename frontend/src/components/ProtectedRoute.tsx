import React, { useEffect, useState } from "react";
import { Spin } from "antd";
import { history } from "umi";
import { isAuthenticated, getCurrentUser, User } from "../utils/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated()) {
        history.push("/login");
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        } else {
          history.push("/login");
        }
      } catch (error) {
        console.error("认证检查失败:", error);
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
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Spin size="large" tip="验证用户身份..." />
      </div>
    );
  }

  return user ? <>{children}</> : null;
};

export default ProtectedRoute;

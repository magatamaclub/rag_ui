import React, { useState } from "react";
import { Form, Input, Button, Card, message, Tabs } from "antd";
import { UserOutlined, LockOutlined, MailOutlined } from "@ant-design/icons";
import { history } from "umi";
import { request } from "@/utils/request";

const { TabPane } = Tabs;

interface LoginFormData {
  username: string;
  password: string;
}

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const LoginPage: React.FC = () => {
  const [loginLoading, setLoginLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("login");

  const handleLogin = async (values: LoginFormData) => {
    setLoginLoading(true);
    try {
      const response = await request("/api/v1/auth/login", {
        method: "POST",
        data: {
          username: values.username,
          password: values.password,
        },
      });

      if (response.access_token) {
        // 存储token到localStorage
        localStorage.setItem("access_token", response.access_token);
        localStorage.setItem("token_type", response.token_type);

        message.success("登录成功！");

        // 跳转到主页
        history.push("/");
      }
    } catch (error: any) {
      console.error("Login error:", error);
      if (error.response?.status === 401) {
        message.error("用户名或密码错误");
      } else {
        message.error("登录失败，请稍后重试");
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (values: RegisterFormData) => {
    if (values.password !== values.confirmPassword) {
      message.error("两次输入的密码不一致");
      return;
    }

    setRegisterLoading(true);
    try {
      const response = await request("/api/v1/auth/register", {
        method: "POST",
        data: {
          username: values.username,
          email: values.email,
          password: values.password,
        },
      });

      if (response.id) {
        message.success("注册成功！请登录");
        setActiveTab("login");
      }
    } catch (error: any) {
      console.error("Register error:", error);
      if (error.response?.status === 400) {
        const detail = error.response?.data?.detail || "注册失败";
        message.error(detail);
      } else {
        message.error("注册失败，请稍后重试");
      }
    } finally {
      setRegisterLoading(false);
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
          borderRadius: "8px",
        }}
        title={
          <div
            style={{
              textAlign: "center",
              fontSize: "24px",
              fontWeight: "bold",
            }}
          >
            RAG UI 系统
          </div>
        }
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab} centered>
          <TabPane tab="登录" key="login">
            <Form
              name="login"
              onFinish={handleLogin}
              autoComplete="off"
              layout="vertical"
            >
              <Form.Item
                name="username"
                rules={[{ required: true, message: "请输入用户名!" }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[{ required: true, message: "请输入密码!" }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loginLoading}
                  block
                  size="large"
                  style={{ marginTop: "16px" }}
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="注册" key="register">
            <Form
              name="register"
              onFinish={handleRegister}
              autoComplete="off"
              layout="vertical"
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: "请输入用户名!" },
                  { min: 3, message: "用户名至少3个字符!" },
                ]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="email"
                rules={[
                  { required: true, message: "请输入邮箱!" },
                  { type: "email", message: "请输入有效的邮箱地址!" },
                ]}
              >
                <Input
                  prefix={<MailOutlined />}
                  placeholder="邮箱"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: "请输入密码!" },
                  { min: 6, message: "密码至少6个字符!" },
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                rules={[{ required: true, message: "请确认密码!" }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="确认密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={registerLoading}
                  block
                  size="large"
                  style={{ marginTop: "16px" }}
                >
                  注册
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default LoginPage;

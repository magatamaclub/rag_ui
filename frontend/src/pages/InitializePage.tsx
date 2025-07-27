import React, { useState, useEffect } from "react";
import {
  Card,
  Button,
  Steps,
  Alert,
  Spin,
  message,
  Typography,
  Space,
} from "antd";
import {
  CheckCircleOutlined,
  DatabaseOutlined,
  UserOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { request } from "@/utils/request";
import { history } from "umi";

const { Title, Paragraph } = Typography;
const { Step } = Steps;

interface DatabaseStatus {
  is_initialized: boolean;
  has_connection: boolean;
  has_tables: boolean;
  has_admin_user: boolean;
  message: string;
}

const InitializePage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [status, setStatus] = useState<DatabaseStatus | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  // 检查数据库状态
  const checkDatabaseStatus = async () => {
    setLoading(true);
    try {
      const response = (await request("/api/v1/database/status", {
        method: "GET",
      })) as DatabaseStatus;
      setStatus(response);

      if (response.is_initialized) {
        message.success("数据库已初始化完成");
        setTimeout(() => {
          history.push("/login");
        }, 2000);
      } else {
        // 根据状态设置当前步骤
        if (!response.has_connection) {
          setCurrentStep(0);
        } else if (!response.has_tables) {
          setCurrentStep(1);
        } else if (!response.has_admin_user) {
          setCurrentStep(2);
        }
      }
    } catch (error) {
      message.error("检查数据库状态失败");
      console.error("Database status check failed:", error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化数据库
  const initializeDatabase = async () => {
    setInitializing(true);
    try {
      const response = await request("/api/v1/database/initialize", {
        method: "POST",
      });

      if (response.success) {
        message.success("数据库初始化成功！");
        setTimeout(() => {
          history.push("/login");
        }, 2000);
      }
    } catch (error) {
      message.error("数据库初始化失败");
      console.error("Database initialization failed:", error);
    } finally {
      setInitializing(false);
    }
  };

  useEffect(() => {
    checkDatabaseStatus();
  }, []);

  const steps = [
    {
      title: "数据库连接",
      description: "检查数据库连接状态",
      icon: <DatabaseOutlined />,
      status: status?.has_connection ? "finish" : "error",
    },
    {
      title: "创建数据表",
      description: "创建应用所需的数据表结构",
      icon: <SettingOutlined />,
      status: status?.has_tables
        ? "finish"
        : status?.has_connection
          ? "process"
          : "wait",
    },
    {
      title: "创建管理员",
      description: "创建默认管理员用户",
      icon: <UserOutlined />,
      status: status?.has_admin_user
        ? "finish"
        : status?.has_tables
          ? "process"
          : "wait",
    },
    {
      title: "初始化完成",
      description: "系统准备就绪",
      icon: <CheckCircleOutlined />,
      status: status?.is_initialized ? "finish" : "wait",
    },
  ];

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
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f0f2f5",
        padding: "50px 20px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Card
        style={{
          width: "100%",
          maxWidth: 800,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <Title level={2}>
            <DatabaseOutlined style={{ marginRight: 8 }} />
            数据库初始化
          </Title>
          <Paragraph type="secondary">
            首次使用需要初始化数据库，请按照以下步骤完成设置
          </Paragraph>
        </div>

        {status && (
          <Alert
            message={status.message}
            type={status.is_initialized ? "success" : "warning"}
            style={{ marginBottom: 30 }}
            showIcon
          />
        )}

        <Steps
          current={currentStep}
          direction="vertical"
          style={{ marginBottom: 40 }}
        >
          {steps.map((step, index) => (
            <Step
              key={index}
              title={step.title}
              description={step.description}
              icon={step.icon}
              status={step.status as any}
            />
          ))}
        </Steps>

        <div style={{ textAlign: "center" }}>
          <Space direction="vertical" size="large">
            {!status?.is_initialized && (
              <Button
                type="primary"
                size="large"
                loading={initializing}
                onClick={initializeDatabase}
                disabled={!status?.has_connection}
                style={{ width: 200 }}
              >
                开始初始化
              </Button>
            )}

            <Button
              size="large"
              onClick={checkDatabaseStatus}
              disabled={initializing}
              style={{ width: 200 }}
            >
              重新检查状态
            </Button>

            {status?.is_initialized && (
              <Button
                type="primary"
                size="large"
                onClick={() => history.push("/login")}
                style={{ width: 200 }}
              >
                前往登录
              </Button>
            )}
          </Space>
        </div>

        {status?.is_initialized && (
          <Alert
            message="数据库初始化完成"
            description={
              <div>
                <p>默认管理员账户信息：</p>
                <p>
                  <strong>用户名:</strong> admin
                </p>
                <p>
                  <strong>密码:</strong> admin123
                </p>
                <p>请及时修改默认密码以确保安全。</p>
              </div>
            }
            type="success"
            style={{ marginTop: 30 }}
            showIcon
          />
        )}
      </Card>
    </div>
  );
};

export default InitializePage;

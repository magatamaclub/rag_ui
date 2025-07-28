import React, { useState, useEffect } from "react";
import {
  Layout,
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  message,
  Space,
  Tag,
  Popconfirm,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { authenticatedRequest, getCurrentUser, User } from "../utils/auth";

const { Header, Content } = Layout;
const { Option } = Select;

interface DifyApp {
  id: number;
  name: string;
  app_type: string;
  api_url: string;
  api_key: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

const appTypeColors: Record<string, string> = {
  workflow: "blue",
  chatflow: "green",
  chatbot: "orange",
  agent: "purple",
  text_generator: "cyan",
};

const appTypeLabels: Record<string, string> = {
  workflow: "工作流",
  chatflow: "聊天流",
  chatbot: "聊天机器人",
  agent: "智能代理",
  text_generator: "文本生成器",
};

const DifyAppManagePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [apps, setApps] = useState<DifyApp[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingApp, setEditingApp] = useState<DifyApp | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    // Check if user is admin
    const loadUser = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        if (!currentUser || currentUser.role !== "admin") {
          message.error("需要管理员权限才能访问此页面");
          window.location.href = "/chat";
          return;
        }
        await loadApps();
      } catch (error) {
        console.error("获取用户信息失败:", error);
        window.location.href = "/login";
      }
    };
    loadUser();
  }, []);

  const loadApps = async () => {
    setLoading(true);
    try {
      const data = await authenticatedRequest("/api/v1/dify-apps");
      setApps(data);
    } catch (error: any) {
      console.error("Error loading apps:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        window.location.href = "/login";
      } else {
        message.error("加载应用列表时发生错误");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApp = () => {
    setEditingApp(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditApp = (app: DifyApp) => {
    setEditingApp(app);
    form.setFieldsValue(app);
    setModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const url = editingApp
        ? `/api/v1/dify-apps/${editingApp.id}`
        : "/api/v1/dify-apps";
      const method = editingApp ? "PUT" : "POST";

      const data = await authenticatedRequest(url, {
        method,
        data: values,
      });

      message.success(editingApp ? "应用更新成功" : "应用创建成功");
      setModalVisible(false);
      await loadApps();
    } catch (error: any) {
      console.error("Error submitting app:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        window.location.href = "/login";
      } else {
        message.error(error.message || "操作时发生错误");
      }
    }
  };

  const handleDeleteApp = async (appId: number) => {
    try {
      await authenticatedRequest(`/api/v1/dify-apps/${appId}`, {
        method: "DELETE",
      });

      message.success("应用删除成功");
      await loadApps();
    } catch (error: any) {
      console.error("Error deleting app:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        window.location.href = "/login";
      } else {
        message.error("删除应用时发生错误");
      }
    }
  };

  const columns = [
    {
      title: "应用名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "应用类型",
      dataIndex: "app_type",
      key: "app_type",
      render: (type: string) => (
        <Tag color={appTypeColors[type]}>{appTypeLabels[type] || type}</Tag>
      ),
    },
    {
      title: "API URL",
      dataIndex: "api_url",
      key: "api_url",
      ellipsis: true,
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      ellipsis: true,
    },
    {
      title: "状态",
      dataIndex: "is_active",
      key: "is_active",
      render: (isActive: boolean) => (
        <Tag color={isActive ? "green" : "red"}>
          {isActive ? "活跃" : "禁用"}
        </Tag>
      ),
    },
    {
      title: "操作",
      key: "actions",
      render: (_: any, record: DifyApp) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditApp(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个应用吗？"
            onConfirm={() => handleDeleteApp(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (!user || user.role !== "admin") {
    return null;
  }

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          background: "#fff",
          padding: "0 20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <h2 style={{ margin: 0, color: "#1890ff" }}>Dify 应用管理</h2>
        <Button type="text" icon={<UserOutlined />}>
          {user.username} (管理员)
        </Button>
      </Header>
      <Content style={{ padding: "24px" }}>
        <Card
          title="Dify 应用列表"
          extra={
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateApp}
            >
              创建应用
            </Button>
          }
        >
          <Table
            columns={columns}
            dataSource={apps}
            loading={loading}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        </Card>

        <Modal
          title={editingApp ? "编辑应用" : "创建应用"}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          footer={null}
          width={600}
        >
          <Form form={form} onFinish={handleSubmit} layout="vertical">
            <Form.Item
              name="name"
              label="应用名称"
              rules={[{ required: true, message: "请输入应用名称" }]}
            >
              <Input placeholder="输入应用名称" />
            </Form.Item>

            <Form.Item
              name="app_type"
              label="应用类型"
              rules={[{ required: true, message: "请选择应用类型" }]}
            >
              <Select placeholder="选择应用类型">
                <Option value="workflow">工作流</Option>
                <Option value="chatflow">聊天流</Option>
                <Option value="chatbot">聊天机器人</Option>
                <Option value="agent">智能代理</Option>
                <Option value="text_generator">文本生成器</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="api_url"
              label="API URL"
              rules={[
                { required: true, message: "请输入API URL" },
                { type: "url", message: "请输入有效的URL" },
              ]}
            >
              <Input placeholder="https://api.dify.ai/v1" />
            </Form.Item>

            <Form.Item
              name="api_key"
              label="API Key"
              rules={[{ required: true, message: "请输入API Key" }]}
            >
              <Input.Password placeholder="输入API Key" />
            </Form.Item>

            <Form.Item name="description" label="描述">
              <Input.TextArea rows={3} placeholder="输入应用描述（可选）" />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  {editingApp ? "更新" : "创建"}
                </Button>
                <Button onClick={() => setModalVisible(false)}>取消</Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
};

export default DifyAppManagePage;

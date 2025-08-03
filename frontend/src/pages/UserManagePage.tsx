import React, { useState, useEffect } from "react";
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Space,
  message,
  Card,
  Layout,
  Typography,
  Popconfirm,
  Tag,
  Row,
  Col,
  Dropdown,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  MailOutlined,
  SafetyOutlined,
  HomeOutlined,
  MessageOutlined,
  LogoutOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { history } from "umi";
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  User,
  UserCreate,
  UserUpdate,
  UserListResponse,
} from "../utils/userApi";
import { getCurrentUser, User as AuthUser, logout } from "../utils/auth";

const { Header, Content } = Layout;
const { Title } = Typography;
const { Option } = Select;

const UserManagePage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const [form] = Form.useForm();

  useEffect(() => {
    checkAdminPermission();
  }, []);

  const checkAdminPermission = async () => {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      if (!user || user.role !== "admin") {
        message.error("需要管理员权限才能访问此页面");
        history.push("/chat");
        return;
      }
      await loadUsers();
    } catch (error) {
      console.error("获取用户信息失败:", error);
      message.error("获取用户信息失败，请重新登录");
      history.push("/login");
    }
  };

  const loadUsers = async (page: number = 1, size: number = 20) => {
    setLoading(true);
    try {
      const response: UserListResponse = await getUserList(page, size);
      setUsers(response.users);
      setPagination({
        current: response.page,
        pageSize: response.size,
        total: response.total,
      });
    } catch (error: any) {
      console.error("加载用户列表失败:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        history.push("/login");
      } else {
        message.error("加载用户列表失败");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setEditingUser(null);
    form.resetFields();
    form.setFieldsValue({ role: "user", is_active: true });
    setModalVisible(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    });
    setModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        // 更新用户
        const updateData: UserUpdate = {
          username: values.username,
          email: values.email,
          role: values.role,
          is_active: values.is_active,
        };
        await updateUser(editingUser.id, updateData);
        message.success("用户更新成功");
      } else {
        // 创建用户
        const createData: UserCreate = {
          username: values.username,
          email: values.email,
          password: values.password,
          role: values.role,
        };
        await createUser(createData);
        message.success("用户创建成功");
      }
      setModalVisible(false);
      await loadUsers(pagination.current, pagination.pageSize);
    } catch (error: any) {
      console.error("操作失败:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        history.push("/login");
      } else {
        message.error(error.message || "操作失败");
      }
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      await deleteUser(userId);
      message.success("用户删除成功");
      await loadUsers(pagination.current, pagination.pageSize);
    } catch (error: any) {
      console.error("删除用户失败:", error);
      if (error.message?.includes("401") || error.response?.status === 401) {
        message.error("认证失败，请重新登录");
        history.push("/login");
      } else {
        message.error(error.message || "删除用户失败");
      }
    }
  };

  const handleTableChange = (page: number, pageSize?: number) => {
    loadUsers(page, pageSize || pagination.pageSize);
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      width: 80,
    },
    {
      title: "用户名",
      dataIndex: "username",
      key: "username",
      render: (text: string) => (
        <Space>
          <UserOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: "邮箱",
      dataIndex: "email",
      key: "email",
      render: (text: string) => (
        <Space>
          <MailOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: "角色",
      dataIndex: "role",
      key: "role",
      render: (role: string) => (
        <Tag
          color={role === "admin" ? "red" : "blue"}
          icon={<SafetyOutlined />}
        >
          {role === "admin" ? "管理员" : "普通用户"}
        </Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "is_active",
      key: "is_active",
      render: (isActive: boolean) => (
        <Tag color={isActive ? "green" : "red"}>
          {isActive ? "激活" : "禁用"}
        </Tag>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (text: string) =>
        text ? new Date(text).toLocaleString("zh-CN") : "-",
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: User) => (
        <Space size="middle">
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditUser(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
            description="删除后将无法恢复。"
            onConfirm={() => handleDeleteUser(record.id)}
            okText="确定"
            cancelText="取消"
            disabled={currentUser?.id === record.id}
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
              disabled={currentUser?.id === record.id}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          background: "#fff",
          padding: "0 24px",
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={3} style={{ margin: 0 }}>
              用户管理
            </Title>
          </Col>
          <Col>
            <Button onClick={() => history.push("/chat")}>返回主页</Button>
          </Col>
        </Row>
      </Header>
      <Content style={{ padding: "24px" }}>
        <Card>
          <Space style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateUser}
            >
              添加用户
            </Button>
          </Space>

          <Table
            columns={columns}
            dataSource={users}
            rowKey="id"
            loading={loading}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              onChange: handleTableChange,
              onShowSizeChange: handleTableChange,
            }}
          />
        </Card>

        <Modal
          title={editingUser ? "编辑用户" : "添加用户"}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          footer={null}
          width={600}
        >
          <Form form={form} layout="vertical" onFinish={handleSubmit}>
            <Form.Item
              label="用户名"
              name="username"
              rules={[
                { required: true, message: "请输入用户名" },
                { min: 3, message: "用户名至少3个字符" },
                { max: 20, message: "用户名最多20个字符" },
              ]}
            >
              <Input placeholder="请输入用户名" />
            </Form.Item>

            <Form.Item
              label="邮箱"
              name="email"
              rules={[
                { required: true, message: "请输入邮箱" },
                { type: "email", message: "请输入有效的邮箱地址" },
              ]}
            >
              <Input placeholder="请输入邮箱地址" />
            </Form.Item>

            {!editingUser && (
              <Form.Item
                label="密码"
                name="password"
                rules={[
                  { required: true, message: "请输入密码" },
                  { min: 6, message: "密码至少6个字符" },
                ]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            )}

            <Form.Item
              label="角色"
              name="role"
              rules={[{ required: true, message: "请选择角色" }]}
            >
              <Select placeholder="请选择用户角色">
                <Option value="user">普通用户</Option>
                <Option value="admin">管理员</Option>
              </Select>
            </Form.Item>

            {editingUser && (
              <Form.Item
                label="账户状态"
                name="is_active"
                valuePropName="checked"
              >
                <Switch checkedChildren="激活" unCheckedChildren="禁用" />
              </Form.Item>
            )}

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  {editingUser ? "更新" : "创建"}
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

export default UserManagePage;

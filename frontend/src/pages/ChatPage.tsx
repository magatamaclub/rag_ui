import React, { useState, useRef, useEffect } from "react";
import {
  Layout,
  Menu,
  Input,
  Button,
  List,
  Avatar,
  Card,
  Space,
  Dropdown,
  message,
  Select,
} from "antd";
import {
  SendOutlined,
  PlusOutlined,
  MessageOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import {
  authenticatedRequest,
  getCurrentUser,
  logout,
  User,
} from "../utils/auth";

const { Sider, Content, Header } = Layout;
const { TextArea } = Input;
const { Option } = Select;

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
}

interface RetrieverResult {
  id: string;
  content: string;
  metadata: { [key: string]: any };
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  retrieverResults?: RetrieverResult[];
}

interface DifyApp {
  id: number;
  name: string;
  app_type: string;
  api_url: string;
  description?: string;
  is_active: boolean;
}

const ChatPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [difyApps, setDifyApps] = useState<DifyApp[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const savedConversations = localStorage.getItem("chatConversations");
    return savedConversations
      ? JSON.parse(savedConversations)
      : [{ id: "1", title: "New Chat 1", messages: [] }];
  });
  const [currentConversationId, setCurrentConversationId] = useState<string>(
    () => {
      const savedCurrentConversationId = localStorage.getItem(
        "currentChatConversationId"
      );
      return savedCurrentConversationId || "1";
    }
  );
  const [inputMessage, setInputMessage] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentConversation = conversations.find(
    (conv) => conv.id === currentConversationId
  );

  useEffect(() => {
    localStorage.setItem("chatConversations", JSON.stringify(conversations));
    localStorage.setItem("currentChatConversationId", currentConversationId);
  }, [conversations, currentConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // 获取用户信息和Dify应用列表
    const loadUserAndApps = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);

        // 加载Dify应用
        const apps = await authenticatedRequest("/api/v1/dify-apps");
        setDifyApps(apps);
        // 默认选择第一个应用
        if (apps.length > 0) {
          setSelectedAppId(apps[0].id);
        }
      } catch (error) {
        console.error("获取用户信息或应用列表失败:", error);
      }
    };
    loadUserAndApps();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    if (!selectedAppId) {
      message.error("请先选择一个Dify应用");
      return;
    }

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: inputMessage,
    };
    const updatedConversations = conversations.map((conv) =>
      conv.id === currentConversationId
        ? {
            ...conv,
            messages: [...conv.messages, newMessage],
            retrieverResults: [],
          } // Clear previous results
        : conv
    );
    setConversations(updatedConversations);
    setInputMessage("");

    // Add a placeholder for bot response immediately
    const botMessagePlaceholder: Message = {
      id: Date.now().toString() + "-bot",
      sender: "bot",
      text: "",
    };
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === currentConversationId
          ? { ...conv, messages: [...conv.messages, botMessagePlaceholder] }
          : conv
      )
    );

    try {
      // 直接使用 fetch 处理流式响应
      const token = localStorage.getItem("access_token");
      const response = await fetch(`/api/v1/chat/app/${selectedAppId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: newMessage.text,
          // Only send conversation_id if we have an existing Dify conversation ID
          ...(currentConversation?.id && currentConversation.id.includes("-")
            ? { conversation_id: currentConversation.id }
            : {}),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let botResponseText = "";
      let currentRetrieverResults: RetrieverResult[] = [];
      let conversationId = "";

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        console.log("🔄 Received chunk:", chunk);

        // Dify sends data in 'data: {json}\n\n' format
        const lines = chunk
          .split("\n")
          .filter((line) => line.trim().startsWith("data:"));

        for (const line of lines) {
          try {
            const jsonStr = line.substring(5).trim(); // Remove 'data: '
            if (!jsonStr) continue;

            const data = JSON.parse(jsonStr);
            console.log("📦 Parsed data:", data);

            // Handle different event types from Dify workflow
            if (data.event === "message") {
              // This is the main text content from the LLM
              if (data.answer) {
                botResponseText += data.answer;
                console.log("💬 Adding text chunk:", data.answer);

                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          messages: conv.messages.map((msg) =>
                            msg.id === botMessagePlaceholder.id
                              ? { ...msg, text: botResponseText }
                              : msg
                          ),
                        }
                      : conv
                  )
                );
              }
            } else if (data.event === "workflow_started") {
              // Store conversation ID for future requests
              if (data.conversation_id) {
                conversationId = data.conversation_id;
                console.log("🆔 Got conversation ID:", conversationId);
              }
            } else if (data.event === "workflow_finished") {
              console.log("✅ Workflow completed");
              // Final update to ensure we have the complete response
              if (data.data?.outputs?.answer) {
                botResponseText = data.data.outputs.answer;
                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          messages: conv.messages.map((msg) =>
                            msg.id === botMessagePlaceholder.id
                              ? { ...msg, text: botResponseText }
                              : msg
                          ),
                        }
                      : conv
                  )
                );
              }
            } else if (
              data.event === "node_finished" &&
              data.data?.outputs?.result
            ) {
              // Handle knowledge retrieval results
              const retrievalResults = data.data.outputs.result;
              if (Array.isArray(retrievalResults)) {
                currentRetrieverResults = retrievalResults.map(
                  (res: any, index: number) => ({
                    id: res.metadata?.segment_id || `result-${index}`,
                    content: res.content || res.title || "",
                    metadata: res.metadata || {},
                  })
                );

                console.log(
                  "📚 Knowledge retrieval results:",
                  currentRetrieverResults
                );

                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? { ...conv, retrieverResults: currentRetrieverResults }
                      : conv
                  )
                );
              }
            } else if (data.event === "message_end") {
              console.log("🏁 Message stream ended");
              // Update conversation with Dify conversation ID if we got one
              if (conversationId && conversationId !== currentConversationId) {
                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          id: conversationId,
                          title: `Chat ${conversationId.slice(0, 8)}`,
                        }
                      : conv
                  )
                );
                setCurrentConversationId(conversationId);
              }
            }
          } catch (e) {
            console.error("Error parsing Dify stream chunk:", e, "Line:", line);
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Update bot message to show error
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === currentConversationId
            ? {
                ...conv,
                messages: conv.messages.map((msg) =>
                  msg.id === botMessagePlaceholder.id
                    ? { ...msg, text: `Error: ${error}` }
                    : msg
                ),
              }
            : conv
        )
      );
    }
  };

  const handleNewChat = () => {
    const newId = (conversations.length + 1).toString();
    const newConversation: Conversation = {
      id: newId,
      title: `New Chat ${newId}`,
      messages: [],
      retrieverResults: [],
    };
    setConversations([...conversations, newConversation]);
    setCurrentConversationId(newId);
  };

  const handleLogout = () => {
    logout();
  };

  const userMenuItems = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: user?.username || "用户",
    },
    ...(user?.role === "admin"
      ? [
          {
            key: "manage-users",
            icon: <UserOutlined />,
            label: "用户管理",
            onClick: () => (window.location.href = "/user-manage"),
          },
          {
            key: "manage-apps",
            icon: <SettingOutlined />,
            label: "管理Dify应用",
            onClick: () => (window.location.href = "/dify-app-manage"),
          },
        ]
      : []),
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "退出登录",
      onClick: handleLogout,
    },
  ];

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
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <h2 style={{ margin: 0, color: "#1890ff" }}>RAG UI 聊天系统</h2>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewChat}
          >
            新对话
          </Button>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span>选择应用:</span>
            <Select
              style={{ width: 200 }}
              placeholder="选择Dify应用"
              value={selectedAppId}
              onChange={setSelectedAppId}
              notFoundContent={
                difyApps.length === 0
                  ? "暂无Dify应用，请先创建应用"
                  : "无匹配应用"
              }
            >
              {difyApps.map((app) => (
                <Option key={app.id} value={app.id}>
                  {app.name} ({app.app_type})
                </Option>
              ))}
            </Select>
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={async () => {
                try {
                  const apps = await authenticatedRequest("/api/v1/dify-apps");
                  setDifyApps(apps);
                  message.success(`已刷新应用列表 (${apps.length}个应用)`);
                } catch (error) {
                  message.error("刷新应用列表失败");
                }
              }}
            >
              刷新
            </Button>
          </div>
        </div>
        {user && (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Button type="text" icon={<UserOutlined />}>
              {user.username}
            </Button>
          </Dropdown>
        )}
      </Header>
      <Layout>
        <Content
          style={{
            padding: "24px",
            background: "#fff",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ flexGrow: 1, overflowY: "auto", paddingRight: "24px" }}>
            <List
              itemLayout="horizontal"
              dataSource={currentConversation?.messages || []}
              renderItem={(msg) => (
                <List.Item
                  style={{
                    justifyContent:
                      msg.sender === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        src={
                          msg.sender === "user"
                            ? "https://api.dicebear.com/7.x/initials/svg?seed=User"
                            : "https://api.dicebear.com/7.x/initials/svg?seed=Bot"
                        }
                      />
                    }
                    title={msg.sender === "user" ? "You" : "Bot"}
                    description={
                      <Card
                        style={{
                          maxWidth: "70%",
                          background:
                            msg.sender === "user" ? "#e6f7ff" : "#f0f0f0",
                        }}
                      >
                        {msg.text}
                      </Card>
                    }
                    style={{
                      flexDirection:
                        msg.sender === "user" ? "row-reverse" : "row",
                    }}
                  />
                </List.Item>
              )}
            />
            <div ref={messagesEndRef} />
          </div>
          <div style={{ padding: "16px 0", borderTop: "1px solid #f0f0f0" }}>
            <Space.Compact style={{ width: "100%" }}>
              <TextArea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message here..."
                autoSize={{ minRows: 1, maxRows: 5 }}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
              >
                Send
              </Button>
            </Space.Compact>
          </div>
        </Content>
      </Layout>
      <Sider
        width={300}
        theme="light"
        style={{ borderLeft: "1px solid #f0f0f0", padding: "16px" }}
      >
        <h3>Knowledge Sources</h3>
        {currentConversation?.retrieverResults &&
        currentConversation.retrieverResults.length > 0 ? (
          <List
            dataSource={currentConversation.retrieverResults}
            renderItem={(item) => (
              <List.Item>
                <Card
                  size="small"
                  title={item.metadata.title || `Source ${item.id}`}
                  style={{ width: "100%" }}
                >
                  <p>{item.content}</p>
                  {item.metadata.url && (
                    <a
                      href={item.metadata.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Read More
                    </a>
                  )}
                </Card>
              </List.Item>
            )}
          />
        ) : (
          <p>Relevant document snippets will appear here.</p>
        )}
      </Sider>
    </Layout>
  );
};

export default ChatPage;

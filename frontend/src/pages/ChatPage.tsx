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
  Typography,
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
import AuthGuard from "../components/AuthGuard";

const { Sider, Content, Header } = Layout;
const { TextArea } = Input;
const { Option } = Select;
const { Title } = Typography;

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  content: string; // 添加content字段以兼容现有代码
}

interface RetrieverResult {
  id: string;
  content: string;
  text?: string; // 添加可选的text字段
  metadata: { [key: string]: any };
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  retrieverResults?: RetrieverResult[];
  difyConversationId?: string; // 添加Dify会话ID关联
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
    if (savedConversations) {
      try {
        return JSON.parse(savedConversations);
      } catch (e) {
        console.error("Failed to parse saved conversations:", e);
      }
    }
    // 创建默认会话
    return [
      {
        id: "1",
        title: "新对话 1",
        messages: [],
        retrieverResults: [],
        difyConversationId: undefined,
      },
    ];
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
  ) || {
    id: "",
    title: "",
    messages: [],
    retrieverResults: [],
    difyConversationId: undefined,
  };

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
        message.error("获取用户信息失败");
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
      content: inputMessage, // 同时设置content字段
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
      content: "", // 同时设置content字段
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
          // 只有当前会话已经有Dify conversation_id时才发送
          ...(currentConversation.difyConversationId
            ? { conversation_id: currentConversation.difyConversationId }
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
              // 处理新的Dify输出格式
              let responseContent = "";
              let ragData = null;

              // 检查是否有新的格式的数据
              if (data.answer) {
                try {
                  // 尝试解析answer作为JSON
                  const answerData = JSON.parse(data.answer);
                  if (answerData.llm_response) {
                    responseContent = answerData.llm_response;
                    ragData = answerData.rag;
                    console.log("📝 LLM Response:", responseContent);
                    console.log("📚 RAG Data:", ragData);
                  } else {
                    // 如果不是新格式，使用原始answer
                    responseContent = data.answer;
                  }
                } catch (e) {
                  // 如果解析失败，使用原始answer
                  responseContent = data.answer;
                }
              }

              if (responseContent) {
                botResponseText += responseContent;
                console.log("💬 Adding text chunk:", responseContent);

                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          messages: conv.messages.map((msg) =>
                            msg.id === botMessagePlaceholder.id
                              ? {
                                  ...msg,
                                  text: botResponseText,
                                  content: botResponseText,
                                }
                              : msg
                          ),
                        }
                      : conv
                  )
                );
              }

              // 处理RAG数据
              if (ragData && Array.isArray(ragData)) {
                currentRetrieverResults = ragData.map(
                  (res: any, index: number) => ({
                    id: res.metadata?.segment_id || res.id || `result-${index}`,
                    content: res.content || res.text || res.title || "",
                    metadata: res.metadata || {},
                  })
                );

                console.log("📚 Updated RAG results:", currentRetrieverResults);

                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? { ...conv, retrieverResults: currentRetrieverResults }
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
              // 处理最终的工作流输出
              if (data.data?.outputs?.answer) {
                let finalResponseContent = "";
                let finalRagData = null;

                try {
                  // 尝试解析answer作为JSON
                  const answerData = JSON.parse(data.data.outputs.answer);
                  if (answerData.llm_response) {
                    finalResponseContent = answerData.llm_response;
                    finalRagData = answerData.rag;
                    console.log("📝 Final LLM Response:", finalResponseContent);
                    console.log("📚 Final RAG Data:", finalRagData);
                  } else {
                    finalResponseContent = data.data.outputs.answer;
                  }
                } catch (e) {
                  finalResponseContent = data.data.outputs.answer;
                }

                botResponseText = finalResponseContent;
                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          messages: conv.messages.map((msg) =>
                            msg.id === botMessagePlaceholder.id
                              ? {
                                  ...msg,
                                  text: botResponseText,
                                  content: botResponseText,
                                }
                              : msg
                          ),
                        }
                      : conv
                  )
                );

                // 处理最终的RAG数据
                if (finalRagData && Array.isArray(finalRagData)) {
                  currentRetrieverResults = finalRagData.map(
                    (res: any, index: number) => ({
                      id:
                        res.metadata?.segment_id || res.id || `result-${index}`,
                      content: res.content || res.text || res.title || "",
                      metadata: res.metadata || {},
                    })
                  );

                  setConversations((prev) =>
                    prev.map((conv) =>
                      conv.id === currentConversationId
                        ? { ...conv, retrieverResults: currentRetrieverResults }
                        : conv
                    )
                  );
                }
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
              // 保存Dify conversation ID到当前会话，但不改变会话ID
              if (conversationId && !currentConversation.difyConversationId) {
                setConversations((prev) =>
                  prev.map((conv) =>
                    conv.id === currentConversationId
                      ? {
                          ...conv,
                          difyConversationId: conversationId,
                          title:
                            conv.messages.length > 0
                              ? (
                                  conv.messages[0].text ||
                                  conv.messages[0].content ||
                                  ""
                                ).substring(0, 20) + "..."
                              : conv.title,
                        }
                      : conv
                  )
                );
                console.log("💾 Saved Dify conversation ID:", conversationId);
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
                    ? {
                        ...msg,
                        text: `Error: ${error}`,
                        content: `Error: ${error}`,
                      }
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
      title: `新对话 ${newId}`,
      messages: [],
      retrieverResults: [],
      difyConversationId: undefined, // 新对话没有Dify conversation_id
    };
    setConversations([...conversations, newConversation]);
    setCurrentConversationId(newId);
    message.success("已创建新对话");
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
    <Layout style={{ height: "100vh" }}>
      {/* 顶部导航栏 */}
      <Header
        style={{
          backgroundColor: "#fff",
          borderBottom: "1px solid #f0f0f0",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          <Title level={3} style={{ margin: 0, color: "#1890ff" }}>
            RAG UI 聊天系统
          </Title>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
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
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewChat}
          >
            新对话
          </Button>
          {user && (
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Button type="text" icon={<UserOutlined />}>
                {user.username}
              </Button>
            </Dropdown>
          )}
        </div>
      </Header>

      <Layout style={{ height: "calc(100vh - 64px)" }}>
        {/* 左侧会话列表 */}
        <Sider
          width={280}
          style={{
            backgroundColor: "#fafafa",
            borderRight: "1px solid #f0f0f0",
            overflow: "auto",
          }}
        >
          <div style={{ padding: "16px 12px" }}>
            <Title level={5} style={{ margin: "0 0 12px 0", color: "#666" }}>
              会话历史
            </Title>
            <div
              style={{ maxHeight: "calc(100vh - 140px)", overflowY: "auto" }}
            >
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setCurrentConversationId(conv.id)}
                  style={{
                    padding: "12px 16px",
                    marginBottom: "8px",
                    backgroundColor:
                      currentConversationId === conv.id ? "#e6f7ff" : "#fff",
                    border:
                      currentConversationId === conv.id
                        ? "1px solid #1890ff"
                        : "1px solid #f0f0f0",
                    borderRadius: "6px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    if (currentConversationId !== conv.id) {
                      e.currentTarget.style.backgroundColor = "#f5f5f5";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (currentConversationId !== conv.id) {
                      e.currentTarget.style.backgroundColor = "#fff";
                    }
                  }}
                >
                  <div
                    style={{
                      fontSize: "14px",
                      fontWeight:
                        currentConversationId === conv.id ? "500" : "normal",
                      color:
                        currentConversationId === conv.id ? "#1890ff" : "#333",
                      marginBottom: "4px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {conv.title}
                  </div>
                  <div
                    style={{
                      fontSize: "12px",
                      color: "#999",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {conv.messages.length > 0
                      ? (
                          conv.messages[conv.messages.length - 1].content ||
                          conv.messages[conv.messages.length - 1].text ||
                          ""
                        ).substring(0, 30) + "..."
                      : "暂无消息"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Sider>

        {/* 中间聊天区域 */}
        <Content
          style={{
            display: "flex",
            flexDirection: "column",
            backgroundColor: "#fff",
            position: "relative",
          }}
        >
          {/* 聊天消息区域 */}
          <div
            style={{
              flex: 1,
              padding: "20px",
              overflowY: "auto",
              backgroundColor: "#fafafa",
            }}
          >
            {currentConversation.messages.length === 0 ? (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "100%",
                  flexDirection: "column",
                }}
              >
                <div
                  style={{
                    textAlign: "center",
                    color: "#666",
                    fontSize: "16px",
                  }}
                >
                  <div style={{ fontSize: "48px", marginBottom: "16px" }}>
                    💬
                  </div>
                  <div>开始新的对话</div>
                  <div
                    style={{
                      fontSize: "14px",
                      marginTop: "8px",
                      color: "#999",
                    }}
                  >
                    输入您的问题，我来为您解答
                  </div>
                </div>
              </div>
            ) : (
              <List
                itemLayout="horizontal"
                dataSource={currentConversation.messages}
                renderItem={(msg) => (
                  <List.Item
                    style={{
                      justifyContent:
                        msg.sender === "user" ? "flex-end" : "flex-start",
                      marginBottom: "20px",
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
                            backgroundColor:
                              msg.sender === "user" ? "#e6f7ff" : "#f0f0f0",
                            boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
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
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div
            style={{
              padding: "20px",
              backgroundColor: "#fff",
              borderTop: "1px solid #f0f0f0",
            }}
          >
            <Space.Compact style={{ width: "100%" }}>
              <TextArea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="输入您的问题..."
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
                发送
              </Button>
            </Space.Compact>
          </div>
        </Content>

        {/* 右侧知识库面板 */}
        <Sider
          width={300}
          theme="light"
          style={{
            borderLeft: "1px solid #f0f0f0",
            padding: "16px",
            backgroundColor: "#fff",
          }}
        >
          <Title level={5} style={{ marginBottom: "16px" }}>
            相关知识来源
          </Title>

          {currentConversation.retrieverResults &&
          currentConversation.retrieverResults.length > 0 ? (
            <div
              style={{ maxHeight: "calc(100vh - 180px)", overflowY: "auto" }}
            >
              {currentConversation.retrieverResults.map((result, index) => (
                <Card
                  key={index}
                  size="small"
                  style={{
                    marginBottom: "12px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                  }}
                >
                  <div
                    style={{
                      fontSize: "13px",
                      lineHeight: "1.5",
                      color: "#666",
                    }}
                  >
                    {result.content || result.text}
                  </div>
                  {result.metadata && (
                    <div
                      style={{
                        marginTop: "8px",
                        fontSize: "11px",
                        color: "#999",
                        borderTop: "1px solid #f0f0f0",
                        paddingTop: "8px",
                      }}
                    >
                      <div>
                        文档:{" "}
                        {result.metadata.title ||
                          result.metadata.document_name ||
                          "未知"}
                      </div>
                      {result.metadata.url && (
                        <a
                          href={result.metadata.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: "11px" }}
                        >
                          查看更多
                        </a>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          ) : (
            <div
              style={{
                textAlign: "center",
                color: "#999",
                padding: "40px 20px",
              }}
            >
              <div style={{ fontSize: "32px", marginBottom: "12px" }}>📚</div>
              <div>暂无相关知识来源</div>
              <div style={{ fontSize: "12px", marginTop: "8px" }}>
                发送消息后将显示相关资料
              </div>
            </div>
          )}
        </Sider>
      </Layout>
    </Layout>
  );
};

const ProtectedChatPage: React.FC = () => {
  return (
    <AuthGuard>
      <ChatPage />
    </AuthGuard>
  );
};

export default ProtectedChatPage;

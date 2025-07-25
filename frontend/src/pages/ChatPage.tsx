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
} from "antd";
import {
  SendOutlined,
  PlusOutlined,
  MessageOutlined,
  UserOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import {
  authenticatedRequest,
  getCurrentUser,
  logout,
  User,
} from "../utils/auth";

const { Sider, Content, Header } = Layout;
const { TextArea } = Input;

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

const ChatPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
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
    // 获取用户信息
    const loadUser = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error("获取用户信息失败:", error);
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

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
      const response = await authenticatedRequest("/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: newMessage.text,
          conversation_id: currentConversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let botResponseText = "";
      let currentRetrieverResults: RetrieverResult[] = [];

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        // Dify sends data in 'data: {json}\n\n' format
        const lines = chunk
          .split("\n")
          .filter((line) => line.startsWith("data:"));
        for (const line of lines) {
          try {
            const data = JSON.parse(line.substring(5)); // Remove 'data: '
            if (data.event === "text_chunk") {
              botResponseText += data.answer;
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
            } else if (data.event === "llm_end") {
              // Dify might send final answer in llm_end, but we already accumulated text_chunk
              // If there's a final answer in llm_end, use it, otherwise rely on accumulated text_chunk
              if (data.answer && data.answer.length > botResponseText.length) {
                botResponseText = data.answer;
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
            } else if (data.event === "retriever_result") {
              currentRetrieverResults = data.retriever_results.map(
                (res: any) => ({
                  id: res.id,
                  content: res.content,
                  metadata: res.metadata,
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
          } catch (e) {
            console.error(
              "Error parsing Dify stream chunk:",
              e,
              "Chunk:",
              line
            );
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
        <h2 style={{ margin: 0, color: "#1890ff" }}>RAG UI 聊天系统</h2>
        {user && (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Button type="text" icon={<UserOutlined />}>
              {user.username}
            </Button>
          </Dropdown>
        )}
      </Header>
      <Sider
        width={250}
        theme="light"
        style={{ borderRight: "1px solid #f0f0f0" }}
      >
        <div style={{ padding: "16px", textAlign: "center" }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            block
            onClick={handleNewChat}
          >
            New Chat
          </Button>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentConversationId]}
          onClick={({ key }) => setCurrentConversationId(key as string)}
          style={{ borderRight: 0 }}
        >
          {conversations.map((conv) => (
            <Menu.Item key={conv.id} icon={<MessageOutlined />}>
              {conv.title}
            </Menu.Item>
          ))}
        </Menu>
      </Sider>
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

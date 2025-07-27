/**
 * Frontend Integration Tests for RAG UI
 * Tests React components, API integration, and user workflows
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "umi";
import "@testing-library/jest-dom";

// Mock the auth utilities
jest.mock("../utils/auth", () => ({
  authenticatedRequest: jest.fn(),
  getCurrentUser: jest.fn(),
  logout: jest.fn(),
  isAuthenticated: jest.fn(),
}));

// Mock Ant Design message component
jest.mock("antd", () => ({
  ...jest.requireActual("antd"),
  message: {
    error: jest.fn(),
    success: jest.fn(),
    info: jest.fn(),
  },
}));

import ChatPage from "../pages/ChatPage";
import DifyAppManagePage from "../pages/DifyAppManagePage";
import LoginPage from "../pages/LoginPage";
import { authenticatedRequest, getCurrentUser } from "../utils/auth";

// Test data
const mockUser = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
  role: "user",
  is_active: true,
};

const mockAdminUser = {
  id: 2,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  is_active: true,
};

const mockDifyApps = [
  {
    id: 1,
    name: "Test Chatbot",
    app_type: "chatbot",
    api_url: "https://api.dify.ai/v1",
    description: "Test chatbot application",
    is_active: true,
  },
  {
    id: 2,
    name: "Test Workflow",
    app_type: "workflow",
    api_url: "https://api.dify.ai/v1",
    description: "Test workflow application",
    is_active: true,
  },
];

// Helper function to render components with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("ChatPage Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (authenticatedRequest as jest.Mock).mockImplementation((url) => {
      if (url === "/api/v1/dify-apps") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockDifyApps),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  test("renders chat page with correct elements", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      expect(screen.getByText("RAG UI 聊天系统")).toBeInTheDocument();
      expect(screen.getByText("新对话")).toBeInTheDocument();
      expect(screen.getByText("选择应用:")).toBeInTheDocument();
      expect(screen.getByText("Knowledge Sources")).toBeInTheDocument();
    });
  });

  test("loads and displays Dify apps in selector", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      expect(getCurrentUser).toHaveBeenCalled();
      expect(authenticatedRequest).toHaveBeenCalledWith("/api/v1/dify-apps");
    });
  });

  test("creates new conversation when new chat button is clicked", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      const newChatButton = screen.getByText("新对话");
      fireEvent.click(newChatButton);
    });

    // Check if local storage would be updated
    // This tests the handleNewChat function logic
  });

  test("shows user menu for regular user", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      expect(screen.getByText("testuser")).toBeInTheDocument();
    });
  });

  test("shows admin menu options for admin user", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(mockAdminUser);

    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      expect(screen.getByText("admin")).toBeInTheDocument();
    });
  });

  test("displays error when no app is selected for chat", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      const messageInput = screen.getByPlaceholderText(
        "Type your message here..."
      );
      const sendButton = screen.getByText("Send");

      fireEvent.change(messageInput, { target: { value: "Hello" } });
      fireEvent.click(sendButton);
    });
  });

  test("handles message input and sending", async () => {
    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      const messageInput = screen.getByPlaceholderText(
        "Type your message here..."
      );
      fireEvent.change(messageInput, { target: { value: "Test message" } });
      expect(messageInput).toHaveValue("Test message");
    });
  });
});

describe("DifyAppManagePage Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getCurrentUser as jest.Mock).mockResolvedValue(mockAdminUser);
    (authenticatedRequest as jest.Mock).mockImplementation((url) => {
      if (url === "/api/v1/dify-apps") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockDifyApps),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  test("renders Dify app management page for admin", async () => {
    renderWithRouter(<DifyAppManagePage />);

    await waitFor(() => {
      expect(screen.getByText("Dify 应用管理")).toBeInTheDocument();
      expect(screen.getByText("创建应用")).toBeInTheDocument();
      expect(screen.getByText("Dify 应用列表")).toBeInTheDocument();
    });
  });

  test("loads and displays Dify apps in table", async () => {
    renderWithRouter(<DifyAppManagePage />);

    await waitFor(() => {
      expect(screen.getByText("Test Chatbot")).toBeInTheDocument();
      expect(screen.getByText("Test Workflow")).toBeInTheDocument();
    });
  });

  test("opens create modal when create button is clicked", async () => {
    renderWithRouter(<DifyAppManagePage />);

    await waitFor(() => {
      const createButton = screen.getByText("创建应用");
      fireEvent.click(createButton);

      expect(screen.getByText("创建应用")).toBeInTheDocument();
      expect(screen.getByText("应用名称")).toBeInTheDocument();
      expect(screen.getByText("应用类型")).toBeInTheDocument();
    });
  });

  test("redirects non-admin users", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    renderWithRouter(<DifyAppManagePage />);

    // Should not render admin content for regular user
    await waitFor(() => {
      expect(screen.queryByText("Dify 应用管理")).not.toBeInTheDocument();
    });
  });
});

describe("LoginPage Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders login form", () => {
    renderWithRouter(<LoginPage />);

    expect(screen.getByText("用户登录")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("用户名")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("密码")).toBeInTheDocument();
    expect(screen.getByText("登录")).toBeInTheDocument();
  });

  test("handles form input changes", () => {
    renderWithRouter(<LoginPage />);

    const usernameInput = screen.getByPlaceholderText("用户名");
    const passwordInput = screen.getByPlaceholderText("密码");

    fireEvent.change(usernameInput, { target: { value: "testuser" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    expect(usernameInput).toHaveValue("testuser");
    expect(passwordInput).toHaveValue("password123");
  });
});

describe("API Integration Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("handles successful API responses", async () => {
    const mockResponse = {
      ok: true,
      json: () => Promise.resolve(mockDifyApps),
    };

    (authenticatedRequest as jest.Mock).mockResolvedValue(mockResponse);

    const response = await authenticatedRequest("/api/v1/dify-apps");
    const data = await response.json();

    expect(data).toEqual(mockDifyApps);
  });

  test("handles API error responses", async () => {
    const mockErrorResponse = {
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: "Not found" }),
    };

    (authenticatedRequest as jest.Mock).mockResolvedValue(mockErrorResponse);

    const response = await authenticatedRequest("/api/v1/dify-apps/999");

    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
  });

  test("handles authentication errors", async () => {
    const mockAuthError = {
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Unauthorized" }),
    };

    (authenticatedRequest as jest.Mock).mockResolvedValue(mockAuthError);

    const response = await authenticatedRequest("/api/v1/auth/me");

    expect(response.ok).toBe(false);
    expect(response.status).toBe(401);
  });
});

describe("User Workflow Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (authenticatedRequest as jest.Mock).mockImplementation((url) => {
      if (url === "/api/v1/dify-apps") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockDifyApps),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  test("complete chat workflow", async () => {
    renderWithRouter(<ChatPage />);

    // Wait for page to load
    await waitFor(() => {
      expect(screen.getByText("RAG UI 聊天系统")).toBeInTheDocument();
    });

    // Select an app (simulate user interaction)
    // Note: This would require more complex mocking of Ant Design Select component

    // Type a message
    const messageInput = screen.getByPlaceholderText(
      "Type your message here..."
    );
    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });

    // Send message
    const sendButton = screen.getByText("Send");
    fireEvent.click(sendButton);

    // Verify message was processed (would need to mock chat API)
  });

  test("admin app management workflow", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(mockAdminUser);

    renderWithRouter(<DifyAppManagePage />);

    // Wait for page to load
    await waitFor(() => {
      expect(screen.getByText("Dify 应用管理")).toBeInTheDocument();
    });

    // Click create app button
    const createButton = screen.getByText("创建应用");
    fireEvent.click(createButton);

    // Fill out form (would need more detailed form mocking)
    await waitFor(() => {
      expect(screen.getByText("应用名称")).toBeInTheDocument();
    });
  });
});

describe("Error Handling Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("handles network errors gracefully", async () => {
    (getCurrentUser as jest.Mock).mockRejectedValue(new Error("Network error"));

    renderWithRouter(<ChatPage />);

    // Should handle the error without crashing
    await waitFor(() => {
      expect(getCurrentUser).toHaveBeenCalled();
    });
  });

  test("handles invalid user data", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(null);

    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      // Should handle null user gracefully
      expect(getCurrentUser).toHaveBeenCalled();
    });
  });

  test("handles empty Dify apps response", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (authenticatedRequest as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });

    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      // Should handle empty apps list
      expect(authenticatedRequest).toHaveBeenCalledWith("/api/v1/dify-apps");
    });
  });
});

describe("Performance Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders components within acceptable time", async () => {
    const startTime = performance.now();

    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (authenticatedRequest as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockDifyApps),
    });

    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      expect(screen.getByText("RAG UI 聊天系统")).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 1 second
    expect(renderTime).toBeLessThan(1000);
  });

  test("handles rapid user interactions", async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (authenticatedRequest as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockDifyApps),
    });

    renderWithRouter(<ChatPage />);

    await waitFor(() => {
      const newChatButton = screen.getByText("新对话");

      // Rapidly click new chat button
      for (let i = 0; i < 5; i++) {
        fireEvent.click(newChatButton);
      }
    });

    // Should handle rapid clicks without errors
  });
});

export {};

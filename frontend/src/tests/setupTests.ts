/**
 * Test setup configuration for Jest and React Testing Library
 */

import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock window.location
delete (window as any).location;
window.location = { 
  href: 'http://localhost:3000',
  origin: 'http://localhost:3000',
  pathname: '/',
  search: '',
  hash: ''
} as any;

// Mock Ant Design message notifications
jest.mock('antd', () => ({
  ...jest.requireActual('antd'),
  message: {
    error: jest.fn(),
    success: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
  },
}));

// Mock Umi router
jest.mock('umi', () => ({
  ...jest.requireActual('umi'),
  history: {
    push: jest.fn(),
    replace: jest.fn(),
    goBack: jest.fn(),
  },
}));

// Global test utilities
global.testUtils = {
  createMockUser: (overrides = {}) => ({
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    role: 'user',
    is_active: true,
    ...overrides,
  }),
  
  createMockDifyApp: (overrides = {}) => ({
    id: 1,
    name: 'Test App',
    app_type: 'chatbot',
    api_url: 'https://api.dify.ai/v1',
    api_key: 'test-key',
    description: 'Test application',
    is_active: true,
    ...overrides,
  }),
  
  mockApiResponse: (data: any, ok = true) => ({
    ok,
    json: () => Promise.resolve(data),
    status: ok ? 200 : 400,
  }),
};

// Declare global types for TypeScript
declare global {
  var testUtils: {
    createMockUser: (overrides?: any) => any;
    createMockDifyApp: (overrides?: any) => any;
    mockApiResponse: (data: any, ok?: boolean) => any;
  };
}

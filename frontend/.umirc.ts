
import { defineConfig } from "umi";

export default defineConfig({
  plugins: [
    '@umijs/plugins/dist/access',
    '@umijs/plugins/dist/antd',
    '@umijs/plugins/dist/initial-state',
    '@umijs/plugins/dist/layout',
    '@umijs/plugins/dist/model',
    '@umijs/plugins/dist/request'
  ],
  antd: {},
  access: {},
  model: {},
  initialState: {},
  request: {},
  layout: {
    title: "RAG UI",
  },
  routes: [
    {
      path: '/',
      redirect: '/chat',
    },
    {
      path: '/home',
      component: 'IndexPage',
      name: 'Home',
    },
    {
      path: '/chat',
      component: 'ChatPage',
      name: 'Chat',
    },
    {
      path: '/upload',
      component: 'UploadPage',
      name: 'Upload Documents',
    },
    {
      path: '/dify-config',
      component: 'DifyConfigPage',
      name: 'Dify Config',
    },
  ],
  npmClient: 'pnpm',
  proxy: {
    '/api': {
      'target': 'http://localhost:8000',
      'changeOrigin': true,
    },
  },
});

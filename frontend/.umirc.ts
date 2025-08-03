
import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    {
      path: '/initialize',
      component: '@/pages/InitializePage',
    },
    {
      path: '/login',
      component: '@/pages/LoginPage',
    },
    {
      path: '/',
      redirect: '/chat',
    },
    {
      path: '/chat',
      component: '@/pages/ChatPage',
    },
    {
      path: '/upload',
      component: '@/pages/UploadPage',
    },
    {
      path: '/dify-config',
      component: '@/pages/DifyConfigPage',
    },
    {
      path: '/dify-app-manage',
      component: '@/pages/DifyAppManagePage',
    },
    {
      path: '/user-manage',
      component: '@/pages/UserManagePage',
    },
    {
      path: '/home',
      component: '@/pages/IndexPage',
    },
  ],
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: { '^/api': '/api' },
    },
  },
  title: 'RAG UI 系统',
});


import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
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

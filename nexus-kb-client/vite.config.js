import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers';

function pathResolve(dir) {
  return resolve(process.cwd(), '.', dir);
}

const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig(async () => ({
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        {
          'naive-ui': [
            'useDialog',
            'useMessage',
            'useNotification',
            'useLoadingBar'
          ]
        }
      ]
    }),
    Components({
      resolvers: [ NaiveUiResolver() ]
    })
  ],
  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  resolve: {
    alias: [
      {
        find: '@',
        replacement: pathResolve('src') + '/',
      },
    ],
    dedupe: ['vue'],
  },
  css: {
    preprocessorOptions: {
      less: {
        math: 'always', // 括号内才使用数学计算
        globalVars: {
          // 全局变量
          mainColor: 'red',
        },
      },
    },
  },
  // 1. prevent vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    host: host || false,
    port: 11420,
    strictPort: true,
    proxy: {
      // 带选项写法（对象）
      '/api': {
        target: 'http://127.0.0.1:16088',                      // 从环境变量文件取值
        changeOrigin: true,                             // 支持跨域
        rewrite: (path) => path.replace(/^\/api/, ''),  // 路径重写
      },
      '/static': {
        target: 'http://127.0.0.1:16088',                      // 从环境变量文件取值
        changeOrigin: true,                             // 支持跨域
        rewrite: (path) => path.replace(/^\/api/, ''),  // 路径重写
      },
      '/ws': {
        target: 'ws://127.0.0.1:16088',                      // 从环境变量文件取值
        changeOrigin: true,                             // 支持跨域
        ws: true
      }
    },
    hmr: host
      ? {
          protocol: 'ws',
          host: host,
          port: 11430,
        }
      : undefined,
    watch: {
      // 3. tell vite to ignore watching `src-tauri`
      ignored: ["**/src-tauri/**"],
    },
  },
}));

/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(() => ({
  plugins: [react()],

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  // 1. prevent vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    port: 1420,
    strictPort: true,
    watch: {
      // 3. tell vite to ignore watching `src-tauri`
      ignored: ['**/src-tauri/**'],
    },
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/pages': resolve(__dirname, 'src/pages'),
      '@/hooks': resolve(__dirname, 'src/hooks'),
      '@/services': resolve(__dirname, 'src/services'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/utils': resolve(__dirname, 'src/utils'),
    },
  },

  // Build options
  build: {
    // Tauri supports es2021
    target: process.env.TAURI_PLATFORM == 'windows' ? 'chrome105' : 'safari13',
    // don't minify for debug builds
    minify: !process.env.TAURI_DEBUG ? 'esbuild' as const : false,
    // produce sourcemaps for debug builds
    sourcemap: !!process.env.TAURI_DEBUG,
    
    // Production optimizations
    rollupOptions: {
      output: {
        // 청크 분할 최적화
        manualChunks: {
          // React 관련 라이브러리
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI 라이브러리
          'ui-vendor': ['@chakra-ui/react', '@emotion/react', '@emotion/styled', 'framer-motion'],
          // 차트 라이브러리
          'chart-vendor': ['recharts'],
          // 유틸리티 라이브러리
          'utils-vendor': ['axios', 'date-fns', 'zustand'],
          // 개발 도구 (프로덕션에서 제외)
          ...(process.env.NODE_ENV === 'development' && {
            'dev-vendor': ['@tanstack/react-query']
          })
        },
        // 파일명 최적화
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `js/[name]-[hash].js`;
        },
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || [];
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `images/[name]-[hash][extname]`;
          }
          if (/css/i.test(ext)) {
            return `css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        }
      },
      // 외부 의존성 최적화
      external: process.env.NODE_ENV === 'production' ? [] : undefined
    },
    
    // 빌드 성능 최적화
    chunkSizeWarningLimit: 1000,
    reportCompressedSize: false,
    
    // 에셋 인라인 임계값
    assetsInlineLimit: 4096,
    
    // CSS 코드 분할
    cssCodeSplit: true,
    
    // 빌드 출력 정리
    emptyOutDir: true
  },

  // Test configuration
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    typecheck: {
      tsconfig: './tsconfig.json',
    },
    // 테스트 성능 최적화
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
    // 테스트 파일 패턴
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'src-tauri'],
    // 커버리지 설정
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
      ],
    },
  },

  // 개발 서버 최적화
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@chakra-ui/react',
      '@emotion/react',
      '@emotion/styled',
      'framer-motion',
      '@tanstack/react-query',
      'axios',
      'react-router-dom',
    ],
    exclude: ['@tauri-apps/api'],
  },

  // 환경 변수 설정
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
}))
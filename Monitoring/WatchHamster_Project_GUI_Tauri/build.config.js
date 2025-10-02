/**
 * 빌드 설정 파일
 * 다양한 빌드 시나리오에 대한 설정을 관리합니다.
 */

export const buildConfig = {
  // 기본 설정
  default: {
    minify: true,
    sourcemap: false,
    target: 'es2021',
    outDir: 'dist',
    emptyOutDir: true
  },

  // 개발 빌드
  development: {
    minify: false,
    sourcemap: true,
    target: 'es2021',
    outDir: 'dist-dev',
    emptyOutDir: true,
    define: {
      __DEV__: true,
      __PROD__: false
    }
  },

  // 프로덕션 빌드
  production: {
    minify: 'esbuild',
    sourcemap: false,
    target: 'es2021',
    outDir: 'dist',
    emptyOutDir: true,
    define: {
      __DEV__: false,
      __PROD__: true
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@chakra-ui/react', '@emotion/react', '@emotion/styled'],
          'chart-vendor': ['recharts'],
          'utils-vendor': ['axios', 'date-fns', 'zustand']
        }
      }
    }
  },

  // 테스트 빌드
  test: {
    minify: false,
    sourcemap: true,
    target: 'es2021',
    outDir: 'dist-test',
    emptyOutDir: true,
    define: {
      __DEV__: true,
      __PROD__: false,
      __TEST__: true
    }
  },

  // 플랫폼별 설정
  platforms: {
    windows: {
      target: 'chrome105',
      format: 'es',
      external: []
    },
    macos: {
      target: 'safari13',
      format: 'es',
      external: []
    },
    linux: {
      target: 'chrome105',
      format: 'es',
      external: []
    }
  },

  // 최적화 설정
  optimization: {
    // 번들 크기 최적화
    bundleSize: {
      chunkSizeWarningLimit: 1000,
      assetsInlineLimit: 4096
    },

    // 트리 쉐이킹
    treeShaking: {
      moduleSideEffects: false,
      usedExports: true
    },

    // 코드 분할
    codeSplitting: {
      chunks: 'all',
      minSize: 20000,
      maxSize: 244000,
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true
        }
      }
    }
  },

  // 환경별 변수
  env: {
    development: {
      NODE_ENV: 'development',
      VITE_DEBUG_MODE: 'true',
      VITE_LOG_LEVEL: 'debug'
    },
    production: {
      NODE_ENV: 'production',
      VITE_DEBUG_MODE: 'false',
      VITE_LOG_LEVEL: 'error'
    },
    test: {
      NODE_ENV: 'test',
      VITE_DEBUG_MODE: 'true',
      VITE_LOG_LEVEL: 'debug'
    }
  }
};

// 설정 병합 유틸리티
export function mergeConfig(base, override) {
  return {
    ...base,
    ...override,
    define: {
      ...base.define,
      ...override.define
    },
    rollupOptions: {
      ...base.rollupOptions,
      ...override.rollupOptions,
      output: {
        ...base.rollupOptions?.output,
        ...override.rollupOptions?.output
      }
    }
  };
}

// 환경에 따른 설정 가져오기
export function getConfigForEnvironment(env = 'production') {
  const baseConfig = buildConfig.default;
  const envConfig = buildConfig[env] || buildConfig.production;
  
  return mergeConfig(baseConfig, envConfig);
}

// 플랫폼에 따른 설정 가져오기
export function getConfigForPlatform(platform = 'windows') {
  const platformConfig = buildConfig.platforms[platform] || buildConfig.platforms.windows;
  return platformConfig;
}

export default buildConfig;
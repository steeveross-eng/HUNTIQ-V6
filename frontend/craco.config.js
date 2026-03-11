// craco.config.js
// BRANCHE 2: Production optimizations (98% → 99%)
const path = require("path");
require("dotenv").config();

// Check if we're in development/preview mode (not production build)
// Craco sets NODE_ENV=development for start, NODE_ENV=production for build
const isDevServer = process.env.NODE_ENV !== "production";
const isProduction = process.env.NODE_ENV === "production";

// Environment variable overrides
const config = {
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
  enableVisualEdits: isDevServer, // Only enable during dev server
};

// Conditionally load visual edits modules only in dev mode
let setupDevServer;
let babelMetadataPlugin;

if (config.enableVisualEdits) {
  setupDevServer = require("./plugins/visual-edits/dev-server-setup");
  babelMetadataPlugin = require("./plugins/visual-edits/babel-metadata-plugin");
}

// Conditionally load health check modules only if enabled
let WebpackHealthPlugin;
let setupHealthEndpoints;
let healthPluginInstance;

if (config.enableHealthCheck) {
  WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
  setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
  healthPluginInstance = new WebpackHealthPlugin();
}

// BRANCHE 2: Load compression plugin for production builds
let CompressionPlugin;
if (isProduction) {
  try {
    CompressionPlugin = require("compression-webpack-plugin");
  } catch (e) {
    console.warn("[Build] compression-webpack-plugin not available");
  }
}

const webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {

      // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
        ],
      };

      // Add health check plugin to webpack if enabled
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }
      
      // BRANCHE 2: Production optimizations
      if (isProduction) {
        // Gzip compression for production builds
        if (CompressionPlugin) {
          webpackConfig.plugins.push(
            new CompressionPlugin({
              filename: '[path][base].gz',
              algorithm: 'gzip',
              test: /\.(js|css|html|svg|json)$/,
              threshold: 1024, // Only compress files > 1KB
              minRatio: 0.8,
              deleteOriginalAssets: false,
            })
          );
        }
        
        // Optimize chunk splitting
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          splitChunks: {
            chunks: 'all',
            maxInitialRequests: 25,
            minSize: 20000,
            maxSize: 244000, // ~240KB max per chunk
            cacheGroups: {
              // Vendor chunks
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name(module) {
                  if (!module.context) return 'vendor-misc';
                  const match = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/);
                  if (!match) return 'vendor-misc';
                  const packageName = match[1];
                  // Create separate chunks for large dependencies
                  if (['react', 'react-dom', 'react-router-dom'].includes(packageName)) {
                    return 'vendor-react';
                  }
                  if (['axios', 'date-fns'].includes(packageName)) {
                    return 'vendor-utils';
                  }
                  if (packageName.startsWith('@radix-ui')) {
                    return 'vendor-radix';
                  }
                  if (['leaflet', 'react-leaflet'].includes(packageName)) {
                    return 'vendor-maps';
                  }
                  return 'vendor-misc';
                },
                priority: 10,
                reuseExistingChunk: true,
              },
              // Common code used by multiple chunks
              common: {
                minChunks: 2,
                priority: 5,
                reuseExistingChunk: true,
                name: 'common',
              },
            },
          },
          // Keep runtime code separate
          runtimeChunk: 'single',
        };
        
        // Minimize CSS
        if (webpackConfig.optimization.minimizer) {
          webpackConfig.optimization.minimizer.forEach(minimizer => {
            if (minimizer.constructor.name === 'CssMinimizerPlugin') {
              minimizer.options = {
                ...minimizer.options,
                minimizerOptions: {
                  preset: ['default', { discardComments: { removeAll: true } }],
                },
              };
            }
          });
        }
      }
      
      return webpackConfig;
    },
  },
};

// Only add babel metadata plugin during dev server
if (config.enableVisualEdits && babelMetadataPlugin) {
  webpackConfig.babel = {
    plugins: [babelMetadataPlugin],
  };
}

webpackConfig.devServer = (devServerConfig) => {
  // Apply visual edits dev server setup only if enabled
  if (config.enableVisualEdits && setupDevServer) {
    devServerConfig = setupDevServer(devServerConfig);
  }

  // Add health check endpoints if enabled
  if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
    const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      // Call original setup if exists
      if (originalSetupMiddlewares) {
        middlewares = originalSetupMiddlewares(middlewares, devServer);
      }

      // Setup health endpoints
      setupHealthEndpoints(devServer, healthPluginInstance);

      return middlewares;
    };
  }
  
  // BRANCHE 2: Dev server compression
  devServerConfig.compress = true;

  return devServerConfig;
};

module.exports = webpackConfig;

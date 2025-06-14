const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = (env, argv) => {
    const isProduction = argv.mode === 'production';

    return {
            entry: {
      main: './js/main.js',
      lazy: './js/lazy-load.js'
    },
        output: {
            path: path.resolve(__dirname, 'dist'),
            filename: 'js/[name].[contenthash:8].js',
            clean: true,
            publicPath: '/'
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env'],
                            plugins: ['@babel/plugin-transform-runtime']
                        }
                    }
                },
                {
                    test: /\.css$/,
                    use: [
                        isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
                        'css-loader',
                        'postcss-loader'
                    ]
                },
                {
                    test: /\.(png|jpe?g|gif|webp|svg)$/i,
                    type: 'asset',
                    parser: {
                        dataUrlCondition: {
                            maxSize: 10 * 1024 // 10kb
                        }
                    },
                    generator: {
                        filename: 'images/[name].[contenthash:8][ext]'
                    }
                },
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/i,
                    type: 'asset/resource',
                    generator: {
                        filename: 'fonts/[name].[contenthash:8][ext]'
                    }
                }
            ]
        },
        plugins: [
            new HtmlWebpackPlugin({
                template: './index.html',
                filename: 'index.html',
                chunks: ['main', 'lazy'],
                minify: isProduction ? {
                    removeComments: true,
                    collapseWhitespace: true,
                    removeAttributeQuotes: true,
                    minifyCSS: true,
                    minifyJS: true
                } : false
            }),
            new HtmlWebpackPlugin({
                template: './cart.html',
                filename: 'cart.html',
                chunks: ['main', 'lazy'],
                minify: isProduction ? {
                    removeComments: true,
                    collapseWhitespace: true,
                    removeAttributeQuotes: true,
                    minifyCSS: true,
                    minifyJS: true
                } : false
            }),
            ...(isProduction ? [
                new MiniCssExtractPlugin({
                    filename: 'css/[name].[contenthash:8].css',
                    chunkFilename: 'css/[id].[contenthash:8].css'
                })
            ] : []),
            new CopyWebpackPlugin({
                patterns: [
                    { from: 'images', to: 'images' },
                    { from: 'js/cart-logic.js', to: 'js/cart-logic.js' },
                    { from: 'js/store-selector.js', to: 'js/store-selector.js' },
                    { from: 'components', to: 'components' },
                    { from: 'data', to: 'data' },
                    { from: 'pages', to: 'pages' },
                    { from: 'server.js', to: 'server.js' },
                    { 
                        from: '.env.example', 
                        to: 'env.example',
                        noErrorOnMissing: true
                    },
                    // 複製所有產品頁面
                    { from: 'sp2_product.html', to: 'sp2_product.html', noErrorOnMissing: true },
                    { from: 'sp2_pods_product.html', to: 'sp2_pods_product.html', noErrorOnMissing: true },
                    { from: 'lana_pods_product.html', to: 'lana_pods_product.html', noErrorOnMissing: true },
                    { from: 'lana_a8000_product.html', to: 'lana_a8000_product.html', noErrorOnMissing: true },
                    { from: 'ilia_pods_product.html', to: 'ilia_pods_product.html', noErrorOnMissing: true },
                    { from: 'ilia_leather_product.html', to: 'ilia_leather_product.html', noErrorOnMissing: true },
                    { from: 'ilia_disposable_product.html', to: 'ilia_disposable_product.html', noErrorOnMissing: true },
                    { from: 'ilia_fabric_product.html', to: 'ilia_fabric_product.html', noErrorOnMissing: true },
                    { from: 'ilia_1_product.html', to: 'ilia_1_product.html', noErrorOnMissing: true },
                    { from: 'hta_vape_product.html', to: 'hta_vape_product.html', noErrorOnMissing: true },
                    { from: 'hta_pods_product.html', to: 'hta_pods_product.html', noErrorOnMissing: true },
                    { from: 'order_confirmation.html', to: 'order_confirmation.html', noErrorOnMissing: true },
                    { from: 'cvs_callback.html', to: 'cvs_callback.html', noErrorOnMissing: true },
                    { from: 'test.html', to: 'test.html', noErrorOnMissing: true },
                    { from: 'test-integration.html', to: 'test-integration.html', noErrorOnMissing: true },
                    // 複製產品圖片目錄
                    { from: 'sp2_v', to: 'sp2_v', noErrorOnMissing: true },
                    { from: 'sp2_d', to: 'sp2_d', noErrorOnMissing: true },
                    { from: 'lana_pods', to: 'lana_pods', noErrorOnMissing: true },
                    { from: 'lana_a8000', to: 'lana_a8000', noErrorOnMissing: true },
                    { from: 'illa_d', to: 'illa_d', noErrorOnMissing: true },
                    { from: 'ilia_a_4', to: 'ilia_a_4', noErrorOnMissing: true },
                    { from: 'ilia_L', to: 'ilia_L', noErrorOnMissing: true },
                    { from: 'ilia_1', to: 'ilia_1', noErrorOnMissing: true },
                    { from: 'ilia_Bu', to: 'ilia_Bu', noErrorOnMissing: true },
                    { from: 'hta_vape', to: 'hta_vape', noErrorOnMissing: true },
                    { from: 'hta_pods', to: 'hta_pods', noErrorOnMissing: true }
                ]
            })
        ],
        optimization: {
            minimize: isProduction,
            minimizer: [
                new TerserPlugin({
                    terserOptions: {
                        compress: {
                            drop_console: true,
                            drop_debugger: true
                        },
                        format: {
                            comments: false
                        }
                    },
                    extractComments: false
                }),
                new CssMinimizerPlugin({
                    minimizerOptions: {
                        preset: [
                            'default',
                            {
                                discardComments: { removeAll: true }
                            }
                        ]
                    }
                })
            ],
            splitChunks: {
                chunks: 'all',
                cacheGroups: {
                    styles: {
                        name: 'styles',
                        test: /\.css$/,
                        chunks: 'all',
                        enforce: true
                    },
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: 'vendors',
                        priority: 10
                    },
                    common: {
                        minChunks: 2,
                        priority: 5,
                        reuseExistingChunk: true
                    }
                }
            }
        },
        devServer: {
            static: {
                directory: path.join(__dirname, 'dist')
            },
            compress: true,
            port: 9000,
            hot: true,
            open: true
        },
        performance: {
            hints: isProduction ? 'warning' : false,
            maxEntrypointSize: 512000,
            maxAssetSize: 512000
        }
    };
}; 
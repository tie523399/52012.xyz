module.exports = {
  apps: [{
    name: 'deepvape-app',
    script: './server.js',
    instances: 'max',
    exec_mode: 'cluster',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: '/var/log/pm2/deepvape-error.log',
    out_file: '/var/log/pm2/deepvape-out.log',
    log_file: '/var/log/pm2/deepvape-combined.log',
    time: true,
    merge_logs: true,
    
    // 優雅關閉
    kill_timeout: 5000,
    listen_timeout: 3000,
    
    // 健康檢查
    min_uptime: '10s',
    max_restarts: 10,
    
    // 環境變數
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000,
      NODE_OPTIONS: '--max-old-space-size=1024'
    }
  }],

  deploy: {
    production: {
      user: 'deploy',
      host: 'YOUR_VULTR_IP',
      ref: 'origin/main',
      repo: 'git@github.com:YOUR_USERNAME/deepvape.git',
      path: '/var/www/deepvape',
      'pre-deploy-local': '',
      'post-deploy': 'npm install --production && npm run build:prod && pm2 reload ecosystem.config.js --env production',
      'pre-setup': '',
      ssh_options: 'StrictHostKeyChecking=no'
    }
  }
}; 
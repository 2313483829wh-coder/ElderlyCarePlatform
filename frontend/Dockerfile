FROM node:22-alpine AS build

WORKDIR /app
COPY package*.json ./

# Alpine 下安装构建依赖（sharp 等原生模块需要）
RUN apk add --no-cache build-base python3

# 国内网络：npm 镜像，延长超时、增加重试
ENV SHARP_DIST_BASE_URL=https://npmmirror.com/mirrors/sharp-libvips/
RUN npm config set registry https://registry.npmmirror.com \
    && npm config set fetch-timeout 300000 \
    && npm config set fetch-retries 5

# 必须保留 optional 依赖（rollup 在 alpine 需要 @rollup/rollup-linux-x64-musl）
RUN npm install --include=optional \
    && npm install @rollup/rollup-linux-x64-musl --no-save
COPY . .
# 强制使用相对路径 /api，避免任何 .env 写死绝对地址
ENV VITE_API_BASE=/api
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

FROM node:22-alpine AS build

WORKDIR /app
COPY package*.json ./
# Alpine 下安装构建依赖（如 sharp 等原生模块需要）
RUN apk add --no-cache build-base python3
# 国内网络：npm 与 sharp/libvips 镜像
RUN npm config set registry https://registry.npmmirror.com
ENV SHARP_DIST_BASE_URL=https://npmmirror.com/mirrors/sharp-libvips/
RUN npm install --omit=optional
COPY . .
# 强制使用相对路径 /api，避免任何 .env 写死绝对地址
ENV VITE_API_BASE=/api
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

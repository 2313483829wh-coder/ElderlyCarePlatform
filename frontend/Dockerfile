FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
# 国内网络常超时，启用 npmmirror 加速
RUN npm config set registry https://registry.npmmirror.com
RUN npm install --omit=optional
COPY . .
# 强制使用相对路径 /api，避免任何 .env 写死绝对地址
ENV VITE_API_BASE=/api
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

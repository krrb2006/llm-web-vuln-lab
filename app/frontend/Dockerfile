FROM node:22-alpine AS build
WORKDIR /web
COPY package*.json ./
RUN npm install
COPY . .
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

FROM node:22-alpine
WORKDIR /web
RUN npm install -g serve
COPY --from=build /web/dist ./dist
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]

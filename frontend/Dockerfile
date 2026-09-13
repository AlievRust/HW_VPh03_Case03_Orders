FROM node:22-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM alpine:3.20
COPY --from=build /app/dist /dist

# Build from this directory

# Using node.js 12.2 image
FROM node:16.17.1 as build

# Change workdir and copy package.json
WORKDIR /app
COPY package.json .
COPY package-lock.json .
RUN npm install

# Copy app
COPY . .
RUN ls -lah

# Start the app with npm start
# RUN npm update
RUN npm run build

# Deploy production
FROM nginx:1.19-alpine
COPY --from=build /app/build /usr/share/nginx/html
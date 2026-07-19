# Build stage: compile the Vite app into static assets
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
# `npm ci` requires the lockfile's optional (platform-specific) deps to match
# the build platform exactly; this lockfile was generated on Windows, so it
# doesn't line up with the Linux container's esbuild/rollup binaries. `npm
# install` resolves the right ones for this platform without needing to
# regenerate the lockfile.
RUN npm install

COPY . .

# Vite bakes VITE_* vars into the built JS at build time, so this must be a
# build arg (not a runtime env var) — override it via docker-compose's
# `build.args` (see VITE_API_BASE_URL in the root .env for local vs EC2).
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Serve stage: static files via Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

FROM nginx:alpine

# Копируем файлы фронтенда в папку Nginx
COPY main.html /usr/share/nginx/html/index.html
COPY styles.css /usr/share/nginx/html/
COPY main.js /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем 3000 порт (HTTP)
EXPOSE 3000
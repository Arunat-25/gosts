FROM nginx:alpine

# Копируем файлы фронтенда в папку Nginx
COPY main.html /usr/share/nginx/html/index.html
COPY styles.css /usr/share/nginx/html/
COPY main.js /usr/share/nginx/html/

# Открываем 80 порт (HTTP)
EXPOSE 80
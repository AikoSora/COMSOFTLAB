FROM nginx:alpine

COPY ./docker/admin/etc/nginx/conf.d /etc/nginx/conf.d

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

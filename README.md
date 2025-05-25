# db_project

запуск контейнеров: docker-compose up -d --build

подключение к БД: 
  - через консоль: в Yriy:  docker-compose exec db psql -U admin -d carsharing
  - через pgadmin: host: localhost; port: 5431; user, password: admin; database: carsharing

P.s. 
- таблицы создаются по тексту из db/init/01_create_tables.sql
- это считайте как если этот код вручную ввести в консоль, только тут через /docker-entrypoint-initdb.d 

DROP TABLE if EXISTS pizzas;

CREATE TABLE pizzas (
  id integer primary key autoincrement,
  name text not null,
  description text not null,
  price integer not null
);


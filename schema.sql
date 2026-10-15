-- RezeptBox – MySQL-Schema + Beispieldaten
-- (Die App legt Tabellen sonst auch selbst an.)

CREATE DATABASE IF NOT EXISTS rezeptbox CHARACTER SET utf8mb4;
USE rezeptbox;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100),
  password VARCHAR(100)   -- bewusst Klartext (Schulungslücke)
);

CREATE TABLE IF NOT EXISTS rezepte (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200),
  content TEXT,
  author VARCHAR(100),
  status VARCHAR(50)
);

INSERT INTO users (username, password) VALUES
  ('admin', 'KuechenChef2024'),
  ('mia',   'pommes123'),
  ('ben',   'nudelsalat');

INSERT INTO rezepte (title, content, author, status) VALUES
  ('Omas Apfelkuchen',
   'Zutaten: 4 Äpfel, 200 g Mehl, 150 g Zucker, 3 Eier, 1 Pck. Backpulver.\nZubereitung: Teig verrühren, Äpfel unterheben, bei 180 °C 40 Minuten backen.',
   'mia', 'veröffentlicht'),
  ('Schnelle Tomatensuppe',
   'Zutaten: 1 Dose Tomaten, 1 Zwiebel, Gemüsebrühe, Sahne.\nZubereitung: Zwiebel andünsten, Tomaten + Brühe zugeben, pürieren, mit Sahne verfeinern.',
   'ben', 'veröffentlicht'),
  ('Geheimer Schokokuchen',
   'Zutaten: 200 g Schokolade, 200 g Butter, 4 Eier, 150 g Zucker.\nZubereitung: Schokolade + Butter schmelzen, Rest unterrühren, bei 160 °C 35 Minuten backen.',
   'admin', 'Entwurf');

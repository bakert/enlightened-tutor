CREATE DATABASE enlightened_tutor;

USE enlightened_tutor;

CREATE TABLE IF NOT EXISTS event (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    format VARCHAR(4) NOT NULL,
    date DATETIME NOT NULL,
    level INT NOT NULL,
    num_players INT,
    url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS deck (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rank_high INT,
    rank_low INT,
    player VARCHAR(255) NOT NULL,
    event_id INT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES event(id)
);

CREATE TABLE IF NOT EXISTS deck_card (
    deck_id INT NOT NULL,
    FOREIGN KEY (deck_id) REFERENCES deck(id),
    card VARCHAR(255) NOT NULL,
    num INT NOT NULL,
    sideboard BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS card (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS cube (
    card VARCHAR(255) PRIMARY KEY,
    popularity FLOAT NOT NULL,
    elo INT NOT NULL
);

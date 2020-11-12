CREATE TABLE "ponghi" (
	"id"	INTEGER,
	"file"	TEXT NOT NULL,
	"description"	TEXT,
	"points"	INTEGER DEFAULT 0,
	"sent"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "auth" (
	"key"	TEXT,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("key")
);

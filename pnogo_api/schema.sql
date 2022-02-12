CREATE TABLE "pictures" (
	"id"	INTEGER,
	"file"	TEXT NOT NULL,
	"description"	TEXT,
	"points"	INTEGER DEFAULT 0,
	"sent"	INTEGER DEFAULT 0,
	"daily_date"	TEXT,
	"cndr_id"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "cndr" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "auth" (
	"key"	TEXT,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("key")
);



CREATE TYPE fnd_sts AS ENUM('REQUESTED','FRIENDS','UNRELATED');
CREATE TYPE ord_pos AS ENUM('BTO','STC');
CREATE TYPE ord_res AS ENUM('SUCCESS','FAIL','CANCELLED','PENDING');

-- ---------- Base tables (no foreign keys) ----------

CREATE TABLE "User_Info" (
	"ID"	VARCHAR(16)		NOT NULL,
	"PW"	VARCHAR(255)		NULL,
	"LastConnect"	TIMESTAMPTZ		NULL,
	"Balance"	INT		NULL,
	"Return"	INT		NULL,
	"LastBailout"	INT		NULL,
	"Nickname"	VARCHAR(12)		NULL,
	"Profile"	BYTEA		NULL,
	CONSTRAINT "PK_User_Info" PRIMARY KEY ("ID")
);

CREATE TABLE "Stock_List" (
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	"Stock_Logo"	BYTEA		NULL,
	CONSTRAINT "PK_Stock_List" PRIMARY KEY ("Stock_Name")
);

CREATE TABLE "Quiz" (
	"Quiz_Num"	INT		NOT NULL,
	"Quiz_Body"	JSONB		NULL,
	CONSTRAINT "PK_Quiz" PRIMARY KEY ("Quiz_Num")
);

CREATE TABLE "News_List" (
	"News_ID"	INT		NOT NULL,
	"News_Title"	TEXT		NULL,
	"News_Body"	TEXT		NULL,
	"Reporter"	VARCHAR(10)		NULL,
	"Publisher"	VARCHAR(10)		NULL,
	"News_Date"	TIMESTAMPTZ		NOT NULL,
	CONSTRAINT "PK_News_List" PRIMARY KEY ("News_ID")
);

CREATE TABLE "Notification" (
	"Noti_Num"	INT		NOT NULL,
	"Noti_Head"	TEXT		NULL,
	"Noti_Body"	TEXT		NULL,
	"Noti_Time"	TIMESTAMPTZ		NOT NULL,
	CONSTRAINT "PK_Notification" PRIMARY KEY ("Noti_Num")
);

-- ---------- Tables that depend on the base tables ----------

CREATE TABLE "User_Friends" (
	"FromID"	VARCHAR(16)		NOT NULL,
	"ToID"	VARCHAR(16)		NOT NULL,
	"Friend_Date"	TIMESTAMPTZ		NULL,
	"Friend_Status"	fnd_sts		NULL,
	CONSTRAINT "PK_User_Friends" PRIMARY KEY ("FromID", "ToID"),
	CONSTRAINT "FK_User_Friends_FromID" FOREIGN KEY ("FromID") REFERENCES "User_Info" ("ID"),
	CONSTRAINT "FK_User_Friends_ToID" FOREIGN KEY ("ToID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Stock_Order" (
	"Order_ID"	INT		NOT NULL,
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Order_Quantity"	INT		NULL,
	"Order_Position"	ord_pos		NULL,
	"Order_Result"	ord_res		NULL,
	"Order_Date"	TIMESTAMPTZ		NULL,
	CONSTRAINT "PK_Stock_Order" PRIMARY KEY ("Order_ID"),
	CONSTRAINT "FK_Stock_Order_Stock_Name" FOREIGN KEY ("Stock_Name") REFERENCES "Stock_List" ("Stock_Name"),
	CONSTRAINT "FK_Stock_Order_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Stock_Owned" (
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Own_Quantity"	INT		NULL,
	"Own_PriceChange"	INT		NULL,
	"Own_Avg"	Numeric(12,4)		NULL,
	CONSTRAINT "PK_Stock_Owned" PRIMARY KEY ("Stock_Name", "ID"),
	CONSTRAINT "FK_Stock_Owned_Stock_Name" FOREIGN KEY ("Stock_Name") REFERENCES "Stock_List" ("Stock_Name"),
	CONSTRAINT "FK_Stock_Owned_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "User_Ranking" (
	"ID"	VARCHAR(16)		NOT NULL,
	"Return_Daily"	INT		NULL,
	CONSTRAINT "PK_User_Ranking" PRIMARY KEY ("ID"),
	CONSTRAINT "FK_User_Ranking_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Daily_Snapshot" (
	"Snapshot_Date"	TIMESTAMPTZ		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Total_Asset"	INT		NULL,
	CONSTRAINT "PK_Daily_Snapshot" PRIMARY KEY ("Snapshot_Date", "ID"),
	CONSTRAINT "FK_Daily_Snapshot_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Stock_DailyPrice" (
	"Trade_Date"	TIMESTAMPTZ		NOT NULL,
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	"Open"	INT		NULL,
	"High"	INT		NULL,
	"Low"	INT		NULL,
	"Close"	INT		NULL,
	"Volume"	INT		NULL,
	CONSTRAINT "PK_Stock_DailyPrice" PRIMARY KEY ("Trade_Date", "Stock_Name"),
	CONSTRAINT "FK_Stock_DailyPrice_Stock_Name" FOREIGN KEY ("Stock_Name") REFERENCES "Stock_List" ("Stock_Name")
);

CREATE TABLE "News_Related" (
	"Related_Ord"	INT		NOT NULL,
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	"News_ID"	INT		NOT NULL,
	CONSTRAINT "PK_News_Related" PRIMARY KEY ("Related_Ord", "Stock_Name"),
	CONSTRAINT "FK_News_Related_Stock_Name" FOREIGN KEY ("Stock_Name") REFERENCES "Stock_List" ("Stock_Name"),
	CONSTRAINT "FK_News_Related_News_ID" FOREIGN KEY ("News_ID") REFERENCES "News_List" ("News_ID")
);

-- ---------- Notification link tables (depend on Notification + others) ----------

CREATE TABLE "Notification_Friends" (
	"Noti_Num"	INT		NOT NULL,
	"FromID"	VARCHAR(16)		NOT NULL,
	"ToID"	VARCHAR(16)		NOT NULL,
	CONSTRAINT "PK_Notification_Friends" PRIMARY KEY ("Noti_Num"),
	CONSTRAINT "FK_Notification_Friends_Noti_Num" FOREIGN KEY ("Noti_Num") REFERENCES "Notification" ("Noti_Num"),
	CONSTRAINT "FK_Notification_Friends_FromID" FOREIGN KEY ("FromID") REFERENCES "User_Info" ("ID"),
	CONSTRAINT "FK_Notification_Friends_ToID" FOREIGN KEY ("ToID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Notification_Owned" (
	"Noti_Num"	INT		NOT NULL,
	"Stock_Name"	VARCHAR(20)		NOT NULL,
	CONSTRAINT "PK_Notification_Owned" PRIMARY KEY ("Noti_Num"),
	CONSTRAINT "FK_Notification_Owned_Noti_Num" FOREIGN KEY ("Noti_Num") REFERENCES "Notification" ("Noti_Num"),
	CONSTRAINT "FK_Notification_Owned_Stock_Name" FOREIGN KEY ("Stock_Name") REFERENCES "Stock_List" ("Stock_Name")
);

CREATE TABLE "Notification_Order" (
	"Noti_Num"	INT		NOT NULL,
	"Order_ID"	INT		NOT NULL,
	CONSTRAINT "PK_Notification_Order" PRIMARY KEY ("Noti_Num"),
	CONSTRAINT "FK_Notification_Order_Noti_Num" FOREIGN KEY ("Noti_Num") REFERENCES "Notification" ("Noti_Num"),
	CONSTRAINT "FK_Notification_Order_Order_ID" FOREIGN KEY ("Order_ID") REFERENCES "Stock_Order" ("Order_ID")
);

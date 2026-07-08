

CREATE TYPE fnd_sts AS ENUM('REQUESTED','FRIENDS','UNRELATED');
CREATE TYPE ord_pos AS ENUM('BTO','STC');
CREATE TYPE ord_res AS ENUM('SUCCESS','FAIL','CANCELLED','PENDING');

-- ---------- Base tables (no foreign keys) ----------

CREATE TABLE "User_Info" (
	"ID"	VARCHAR(16)		NOT NULL,
	"PW"	VARCHAR(255)		NULL,
	"Reg_Date"	TIMESTAMPTZ		NULL,
	"Balance"	INT		NULL,
	"Return"	INT		NULL,
	"Last_Bailout_Date"	DATE		NULL,
	"Non_Stock_Cash"	INT		NULL,
	"Nickname"	VARCHAR(12)		NULL,
	"Profile"	BYTEA		NULL,
	CONSTRAINT "PK_User_Info" PRIMARY KEY ("ID")
);

CREATE TABLE "Stock_List" (
	"Stock_Code"	INT		NOT NULL,
	"Stock_Name"	VARCHAR(20)		NULL,
	"Stock_Logo"	BYTEA		NULL,
	"Stock_Desc"	TEXT		NULL,
	CONSTRAINT "PK_Stock_List" PRIMARY KEY ("Stock_Code")
);

-- 종목별 GBM 주가 생성 파라미터. price_generator.py가 이 값으로 하루 안에서 10초 간격 시세를
-- 생성한다. mu/sigma/r은 연 단위(annualized), K는 참고용 기준가(strike류)로 저장한다.
CREATE TABLE "Stock_Params" (
	"Stock_Code"	INT		NOT NULL,
	"Mu"	NUMERIC(10,6)		NULL,
	"Sigma"	NUMERIC(10,6)		NULL,
	"R"	NUMERIC(10,6)		NULL,
	"K"	NUMERIC(14,2)		NULL,
	CONSTRAINT "PK_Stock_Params" PRIMARY KEY ("Stock_Code"),
	CONSTRAINT "FK_Stock_Params_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code")
);

CREATE TABLE "Quiz" (
	"Quiz_Num"	INT		NOT NULL,
	"Quiz_Body"	JSONB		NULL,
	"Quiz_Answer"	INT		NOT NULL,
	CONSTRAINT "PK_Quiz" PRIMARY KEY ("Quiz_Num")
);

CREATE TABLE "News_List" (
	"News_ID"	INT		NOT NULL,
	"News_Title"	TEXT		NULL,
	"News_Body"	TEXT		NULL,
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
	"Stock_Code"	INT		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Order_Quantity"	INT		NULL,
	"Order_Position"	ord_pos		NULL,
	"Order_Result"	ord_res		NULL,
	"Order_Date"	TIMESTAMPTZ		NULL,
	"Order_Price"INT		NULL,
	CONSTRAINT "PK_Stock_Order" PRIMARY KEY ("Order_ID"),
	CONSTRAINT "FK_Stock_Order_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code"),
	CONSTRAINT "FK_Stock_Order_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Stock_Owned" (
	"Stock_Code"	INT		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Own_Quantity"	INT		NULL,
	"Own_PriceChange"	INT		NULL,
	"Own_Avg"	Numeric(12,4)		NULL,
	CONSTRAINT "PK_Stock_Owned" PRIMARY KEY ("Stock_Code", "ID"),
	CONSTRAINT "FK_Stock_Owned_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code"),
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
	"Non_Stock_Cash"	INT		NULL,
	CONSTRAINT "PK_Daily_Snapshot" PRIMARY KEY ("Snapshot_Date", "ID"),
	CONSTRAINT "FK_Daily_Snapshot_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID")
);

CREATE TABLE "Stock_DailyPrice" (
	"Trade_Date"	TIMESTAMPTZ		NOT NULL,
	"Stock_Code"	INT		NOT NULL,
	"Open"	INT		NULL,
	"High"	INT		NULL,
	"Low"	INT		NULL,
	"Close"	INT		NULL,
	"Volume"	INT		NULL,
	CONSTRAINT "PK_Stock_DailyPrice" PRIMARY KEY ("Trade_Date", "Stock_Code"),
	CONSTRAINT "FK_Stock_DailyPrice_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code")
);

CREATE TABLE "News_Related" (
	"News_ID"	INT		NOT NULL,
	"Stock_Code"	INT		NOT NULL,
	CONSTRAINT "PK_News_Related" PRIMARY KEY ("News_ID", "Stock_Code"),
	CONSTRAINT "FK_News_Related_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code"),
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

-- Noti_Num 하나를 여러 사용자가 공유할 수 있어서(같은 종목을 보유한 모든 사람), 수신자별로
-- ID를 따로 두어 (Noti_Num, ID) 단위로 삭제할 수 있게 한다. 그래야 한 사람이 알림을 지워도
-- 그 알림을 같이 받은 다른 사용자 화면에서는 안 사라진다.
CREATE TABLE "Notification_Owned" (
	"Noti_Num"	INT		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Stock_Code"	INT		NOT NULL,
	CONSTRAINT "PK_Notification_Owned" PRIMARY KEY ("Noti_Num", "ID"),
	CONSTRAINT "FK_Notification_Owned_Noti_Num" FOREIGN KEY ("Noti_Num") REFERENCES "Notification" ("Noti_Num"),
	CONSTRAINT "FK_Notification_Owned_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID"),
	CONSTRAINT "FK_Notification_Owned_Stock_Code" FOREIGN KEY ("Stock_Code") REFERENCES "Stock_List" ("Stock_Code")
);

-- 주문 알림은 원래도 수신자가 한 명(주문한 사람)뿐이지만, Owned와 같은 방식으로 통일하고
-- Stock_Order까지 조인하지 않고 바로 수신자를 알 수 있게 ID를 직접 둔다.
CREATE TABLE "Notification_Order" (
	"Noti_Num"	INT		NOT NULL,
	"ID"	VARCHAR(16)		NOT NULL,
	"Order_ID"	INT		NOT NULL,
	CONSTRAINT "PK_Notification_Order" PRIMARY KEY ("Noti_Num", "ID"),
	CONSTRAINT "FK_Notification_Order_Noti_Num" FOREIGN KEY ("Noti_Num") REFERENCES "Notification" ("Noti_Num"),
	CONSTRAINT "FK_Notification_Order_ID" FOREIGN KEY ("ID") REFERENCES "User_Info" ("ID"),
	CONSTRAINT "FK_Notification_Order_Order_ID" FOREIGN KEY ("Order_ID") REFERENCES "Stock_Order" ("Order_ID")
);

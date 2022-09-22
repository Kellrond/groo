drop table if exists test_data;
create table test_data
(
	test_id         SERIAL PRIMARY KEY,
    test_bigint     bigint,
    test_bool       boolean,
    test_bytea      bytea,
    test_char5      char(5),
    test_date       date,
    test_double     double precision,
	test_int        integer,
    test_json       json,
    test_numeric    numeric,
    test_real       real,
    test_smallint   smallint,
    test_time       time,
    test_time_w_tz  timetz,
	test_text       text,
	test_timestamp  timestamp,
    test_varchar5   varchar(5)
);

insert into test_data (
	test_id,    test_bigint,    test_bool,      test_bytea, test_char5,     test_date,  test_double, 
    test_int,   test_json,      test_numeric,   test_real,  test_smallint,  test_time,  test_time_w_tz, 
    test_text,  test_timestamp, test_varchar5
) VALUES (
    0,
    9223372036854775800, 
    true, -- boolean
    decode('013d7d16d7ad4fefb61bd95b765c8ceb', 'hex'), --bytea
    test_char5      char(5),
    test_date       date,
    test_double     double precision,
	test_int        integer,
    test_json       json,
    test_numeric    numeric,
    test_real       real,
    test_smallint   smallint,
    test_time       time,
    test_time_w_tz  timetz,
	test_text       text,
	test_timestamp  timestamp,
    test_varchar5   varchar(5)
)
--Name	Storage Size	Max
--SMALLINT	2 bytes	+32,767
--INTEGER	4 bytes	+2,147,483,647
--BIGINT	8 bytes	+9,223,372,036,854,775,807

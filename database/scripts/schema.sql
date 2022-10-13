-- Documentation Tables
create table if not exists doc_classes
(
	class_id integer primary key,
	file_id integer,
	name text,
	superclass text,
	docstring text,
	parameters text,
	line_start integer,
	line_count integer
);

create table doc_files
(
	file_id integer primary key,
	folder_id integer,
	name text,
	file_path text,
	ext text,
	lines integer
);

create table doc_file_docs
(
	file_id integer primary key,
	docs text
);

create table doc_folders
(
	folder_id integer primary key,
	parent_id integer,
	file_path text,
	name text
);

create table doc_functions
(
	function_id integer primary key,
	parent_id integer,
	file_id integer,
	class_id integer,
	name text,
	parameters text,
	returns text,
	docstring text,
	decorators text,
	line_start integer,
	line_count integer
);

create table doc_imports
(
	import_id integer primary key,
	file_id integer,
	module text,
	object text,
	alias text,
	line_start integer
);


create table doc_todos
(
	todo_id integer primary key,
	file_id integer,
	todo text,
	line_start integer,
	line_count integer
);

create table logs
(
	log_id serial primary key,
	pid integer,
	timestamp timestamp,
	level integer,
	module text,
	log text
);

create table performance_logs
(
	log_id serial primary key,
	pid integer,
	timestamp timestamp,
	start_id integer,
	end_id integer,
	module text,
	name text,
	duration real
);

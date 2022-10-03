-- Documentation Tables
create table if not exists doc_classes
(
	class_id integer primary key,
	file_id integer,
	name text,
	superclass text,
	docstring text,
	parameters text
);

create table doc_dependencies
(
	file_id integer not null,
	module text not null,
	object text,
	dependency_id serial not null
		constraint doc_dependencies_pk
			primary key
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
	name text,
	parameters text,
	returns text,
	docstring text
);

create table doc_routes
(
	file_id integer,
	methods text,
	permissions text,
	url text not null
		constraint dev_routes_pk
			primary key
);

create table logs
(
	log_id serial primary key,
	timestamp timestamp,
	level integer,
	module text,
	log text
);

create table performance_logs
(
	log_id serial primary key,
	timestamp timestamp,
	start_id integer,
	end_id integer,
	module text,
	name text,
	duration real
);






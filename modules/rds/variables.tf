## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
}


variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
}


## Variables unique to ORCA
## REQUIRED
variable "database_app_user_pw" {
  type        = string
  description = "ORCA application database user password."
}


variable "db_deploy_arn" {
  type        = string
  description = "AWS ARN of the db_deploy lambda used to create/modify the DB."
}


variable "db_deploy_source_code_hash" {
  type        = string
  description = "Base 64 SHA-256 hash of the db_deploy lambda used to create/modify the DB."
}


variable "postgres_user_pw" {
  type        = string
  description = "postgres database user password."
}


variable "vpc_postgres_ingress_all_egress_id" {
  description = "The security group of postgres egress ingress"
}


## OPTIONAL - Default variable value is set in ../variables.tf to keep default values centralized.
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
}


## OPTIONAL (DO NOT CHANGE!) - Development use only
## Default variable value is set in ../variables.tf to keep default values centralized.
variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
}

## OPTIONAL Name of admin password to be used for the PostgreSQL DB 
variable "drdb-admin-pass" {
  type = string
  description = "Admin password to be used for the PostgreSQL DB"
}


## OPTIONAL Name of admin password to be used for the PostgreSQL DB 
variable "sm-drdb-admin-pass" {
  type = string
  description = "Admin password to be used for the PostgreSQL DB"
}


## OPTIONAL Name of user password to be used for the PostgreSQL DB 
variable "sm-drdb-user-pass" {
  type = string
  description = "User password to be used for the PostgreSQL DB"
}


## OPTIONAL Name of DB host to be used to connect to PostgreSQL DB 
variable "sm-drdb-host" {
  type = string
  description = "DB host to be used to connect to PostgreSQL DB"
}
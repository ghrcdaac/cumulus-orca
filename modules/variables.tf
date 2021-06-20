## Variables obtained by Cumulus deployment
## Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
## REQUIRED
variable "aws_profile" {
  type        = string
  description = "AWS profile used to deploy the terraform application."
}


variable "buckets" {
  type        = map(object({ name = string, type = string }))
  description = "S3 bucket locations for the various storage types being used."
}


variable "lambda_subnet_ids" {
  type        = list(string)
  description = "List of subnets the lambda functions have access to."
}


variable "permissions_boundary_arn" {
  type        = string
  description = "AWS ARN value for the permission boundary."
}


variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}


variable "system_bucket" {
  type        = string
  description = "Cumulus system bucket used to store internal files."
}


variable "vpc_id" {
  type        = string
  description = "Virtual Private Cloud AWS ID"
}


variable "workflow_config" {
  # https://github.com/nasa/cumulus/blob/master/tf-modules/workflow/variables.tf#L23
  description = "Configuration object with ARNs for workflow integration (Role ARN for executing workflows and Lambda ARNs to trigger on workflow execution)"
  type = object({
    sf_event_sqs_to_db_records_sqs_queue_arn = string
    sf_semaphore_down_lambda_function_arn    = string
    state_machine_role_arn                   = string
    sqs_message_remover_lambda_function_arn  = string
  })
}


## OPTIONAL
variable "region" {
  type        = string
  description = "AWS region to deploy configuration to."
  default     = "us-west-2"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be applied to resources that support tags."
  default     = {}
}


## Variables unique to ORCA
## REQUIRED
variable "database_app_user_pw" {
  type        = string
  description = "ORCA application database user password."
}


variable "orca_default_bucket" {
  type        = string
  description = "Default ORCA S3 Glacier bucket to use if no overrides exist."
}


variable "postgres_user_pw" {
  type        = string
  description = "postgres database user password."
}


## OPTIONAL
variable "database_port" {
  type        = number
  description = "Database port that PostgreSQL traffic will be allowed on."
  default     = 5432
}


variable "orca_ingest_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA copy_to_glacier lambda can use at runtime."
  default     = 2240
}


variable "orca_ingest_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA copy_to_glacier lambda."
  default     = 600
}


variable "orca_recovery_buckets" {
  type        = list(string)
  description = "List of bucket names that ORCA has permissions to restore data to."
  default     = []
}


variable "orca_recovery_complete_filter_prefix" {
  type        = string
  description = "Specifies object key name prefix by the Glacier Bucket trigger."
  default     = ""
}


variable "orca_recovery_expiration_days" {
  type        = number
  description = "Number of days a recovered file will remain available for copy."
  default     = 5
}


variable "orca_recovery_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB the ORCA recovery lambda can use at runtime."
  default     = 128
}


variable "orca_recovery_lambda_timeout" {
  type        = number
  description = "Timeout in number of seconds for ORCA recovery lambdas."
  default     = 300
}


variable "orca_recovery_retry_limit" {
  type        = number
  description = "Maximum number of retries of a recovery failure before giving up."
  default     = 3
}


variable "orca_recovery_retry_interval" {
  type        = number
  description = "Number of seconds to wait between recovery failure retries."
  default     = 1
}

variable "orca_recovery_retry_backoff" {
  type        = number
  description = "The multiplier by which the retry interval increases during each attempt."
  default     = 2
}

variable "sqs_delay_time" {
  type        = number
  description = "The time in seconds that the delivery of all messages in the queue will be delayed."
  default     = 0
}


variable "sqs_maximum_message_size" {
  type        = number
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it."
  default     = 262144
}


variable "staged_recovery_queue_message_retention_time" {
  type        = number
  description = "The number of seconds staged-recovery-queue fifo SQS retains a message in seconds. Maximum value is 14 days."
  default     = 432000 #5 days
}


variable "status_update_queue_message_retention_time" {
  type        = number
  description = "The number of seconds status_update_queue SQS retains a message in seconds. Maximum value is 14 days."
  default     = 777600 #9 days
}


## OPTIONAL (DO NOT CHANGE!) - Development use only
variable "database_app_user" {
  type        = string
  description = "Name of the database application user."
  default     = "orcauser"
}


variable "database_name" {
  type        = string
  description = "Name of the ORCA database in PostgreSQL"
  default     = "disaster_recovery"
}


variable "orca_recovery_retrieval_type" {
  type        = string
  description = "AWS glacier recovery type to use. One of Bulk, Standard, Express."
  default     = "Standard"
}


## Name of admin password to be used for the PostgreSQL DB 
variable "sm_drdb_admin_pass" {
  type = string
  description = "Admin password to be used for the PostgreSQL DB"
  default = "drdb-admin-pass"
}




## OPTIONAL Name of user password to be used for the PostgreSQL DB 
variable "sm_drdb_user_pass" {
  type = string
  description = "User password to be used for the PostgreSQL DB"
  default = "drdb-user-pass"
}

## OPTIONAL Name of DB host to be used to connect to PostgreSQL DB 
variable "sm_drdb_host" {
  type = string
  description = "DB host to be used to connect to PostgreSQL DB"
  default = "drdb-host"
}

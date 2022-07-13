variable "project" {
  description = "Your GCP project ID"
}

variable "credentials" {
  description = "Your credentials file path (.json)"
}

variable "region" {
  description = "Region for GCP resources"
  type        = string
  default     = "asia-southeast1"
}

variable "bq_dataset" {
  description = "BigQuery dataset"
  type        = string
  default     = "networkrail"
}

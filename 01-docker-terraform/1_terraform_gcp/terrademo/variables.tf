variable "credentials" {
    description = "GCloud Credentials File"
    default = "./keys/my-creds.json"
}


variable "project_name" {
    description = "Project name"
    default     = "terraform-demo-435315"
}

variable "region" {
    description = "Region of hosting"
    default="asia-southeast"  
}

variable "zone" {
    description = "Zone"
    default = "asia-southeast1-a"
}

variable "gcs_bucket_name" {
    description = "GCS Bucket Name"
    default = "terraform-demo-435315-gcsbucket"
}

variable "location" {
    description = "Location"
    default="ASIA-SOUTHEAST1"  
}

variable "google_bigquery_dataset_name" {
    description = "Bigquery dataset name on google cloud"
    default="terraform_demo_dataset"
}   

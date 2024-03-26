variable "application_image_repository" {
    description = "The repository of the application image to deploy"
    type        = string
    default     = "localhost/platform-examples-python"
}

variable "application_image_tag" {
    description = "The tag of the application image to deploy"
    type        = string
    default     = "local"
}

variable "application_name" {
    description = "The name of the application"
    type        = string
    default     = "platform-examples-python"
}

variable "application_replicas" {
    description = "The number of replicas to deploy"
    type        = number
    default     = 3
  
}

variable "application_user_id"  {
    description = "The user ID to run the application as"
    type        = number
    default     = 1000
}

variable "deploy_ingress" {
    description = "Deploy an ingress for the application"
    type        = bool
    default     = false
}

variable "local_volume_size" {
    description = "The size of the local volume, in GiB"
    type        = number
    default     = 5
}

variable "namespace" {
    description = "The namespace to deploy the resources to"
    type        = string
    default     = "platform-examples"
}

variable "service_port" {
    description = "The port the service will listen on"
    type        = number
    default     = 8000
}

variable "use_local_volume" {
    description = "Use local volume for storage"
    type        = bool
    default     = true
}
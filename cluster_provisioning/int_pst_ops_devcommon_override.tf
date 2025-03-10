# This override file is used by non-dev deployments on venues used by non-developers for
# testing, PST processing, and operations.ß

variable "hysds_release" {
  default = "v5.0.0-beta.6"
}

variable "lambda_package_release" {
  default = "2.0.0-rc.10.0"
}

variable "pcm_commons_branch" {
  default = "2.0.0-rc.10.0"
}

variable "pcm_branch" {
  default = "2.0.0-rc.10.0"
}

variable "product_delivery_branch" {
  default = "2.0.0-rc.10.0"
}

variable "bach_api_branch" {
  default = "2.0.0-rc.10.0"
}

variable "bach_ui_branch" {
  default = "2.0.0-rc.10.0"
}

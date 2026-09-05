# SCDP Infrastructure — Terraform
# Reproducible cloud infrastructure

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment: development, staging, production"
  type        = string
  default     = "development"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run — Backend
resource "google_cloud_run_v2_service" "backend" {
  name     = "scdp-backend-${var.environment}"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/scdp-backend:latest"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        period_seconds        = 5
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds = 30
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 2 : 0
      max_instance_count = var.environment == "production" ? 10 : 2
    }
  }
}

# Secret Manager — Production secrets
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "scdp-jwt-secret-${var.environment}"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_key" {
  secret_id = "scdp-gemini-key-${var.environment}"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "neo4j_password" {
  secret_id = "scdp-neo4j-password-${var.environment}"
  replication {
    auto {}
  }
}

output "backend_url" {
  value = google_cloud_run_v2_service.backend.uri
}

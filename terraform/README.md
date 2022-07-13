# Setting Up BigQuery Dataset with Terraform

To set up Terraform:

```sh
terraform init
```

To create BigQuery dataset:

```sh
terraform plan -var="project=dtc-de-course-350414" -out tfplan
terraform apply "tfplan"
terraform destroy -var="project=dtc-de-course-350414"
```

To delete after the work and avoid costs on any running services:

```sh
terraform destroy
```

# AP-0150 -- Segmentacion de red como codigo (AWS / Terraform).
#
# Equivalencia en AWS de las zonas del inventario (inventario-segmentacion.yaml):
#   VPC con subnets publicas (DMZ) y privadas (web, app, data, shared), Security Groups que
#   referencian otros SG (no CIDR abierto), y la INVARIANTE de que RDS SQL Server solo acepta
#   1433 desde el SG de la capa de aplicacion. WAF sobre el ALB; egress de datos denegado.
#
# Responsabilidad: el equipo de desarrollo entrega y versiona este IaC; Infraestructura lo
# revisa, aprueba y aplica (terraform apply) con sus cuentas/politicas.

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

resource "aws_vpc" "sufi" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  tags                 = { Name = "vpc-sufi", Proyecto = "SUFI" }
}

# --- Security Group: Capa Web (recibe 443 solo desde el ALB en la DMZ) ---
resource "aws_security_group" "web" {
  name   = "sg-sufi-web"
  vpc_id = aws_vpc.sufi.id
}

resource "aws_security_group" "alb" {
  name   = "sg-sufi-alb"
  vpc_id = aws_vpc.sufi.id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Unico ingreso publico, protegido por WAF.
  }
}

resource "aws_security_group_rule" "web_desde_alb" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.web.id
  source_security_group_id = aws_security_group.alb.id
}

# --- Security Group: Capa Aplicacion (recibe 443 solo desde la capa web) ---
resource "aws_security_group" "app" {
  name   = "sg-sufi-app"
  vpc_id = aws_vpc.sufi.id
}

resource "aws_security_group_rule" "app_desde_web" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.web.id
}

# --- Security Group: Capa de Datos (INVARIANTE: 1433 solo desde el SG de la capa app) ---
resource "aws_security_group" "data" {
  name   = "sg-sufi-data"
  vpc_id = aws_vpc.sufi.id
  # Sin egress a Internet: RDS no necesita salida.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr] # Solo dentro de la VPC.
  }
}

resource "aws_security_group_rule" "data_solo_desde_app" {
  type                     = "ingress"
  from_port                = 1433
  to_port                  = 1433
  protocol                 = "tcp"
  security_group_id        = aws_security_group.data.id
  source_security_group_id = aws_security_group.app.id
}

# --- WAF sobre el ALB (OWASP managed rules) ---
resource "aws_wafv2_web_acl" "sufi" {
  name  = "waf-sufi"
  scope = "REGIONAL"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "waf-sufi"
    sampled_requests_enabled   = true
  }
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "common-rule-set"
      sampled_requests_enabled   = true
    }
  }
}

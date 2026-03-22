# EAM-CHI Gap Analysis

**Project:** CHI Enterprise Asset Management System
**Date:** March 22, 2026
**Domain:** chieam.cubeworksinnovation.com
**Stack:** Nuxt.js (frontend) · FastAPI/Python (backend) · PostgreSQL · Nginx

---

## 1. Executive Summary

This gap analysis evaluates the current state of the CHI EAM system against enterprise asset management best practices, industry standards (ISO 55000, ISO 14224), and security benchmarks. The system was cloned from the ITBA EAM instance and currently provides core asset management, work order, inventory, and procurement workflows. Several gaps exist in infrastructure security, operational maturity, and functional completeness.

---

## 2. Current State Assessment

### 2.1 Identified Modules (from workflow diagrams)

| # | Module | Workflow Exists |
|---|--------|:-:|
| 1 | Asset Record | ✅ |
| 2 | Incident Management | ✅ |
| 3 | Inventory | ✅ |
| 4 | Inventory Adjustment | ✅ |
| 5 | Stock Count | ✅ |
| 6 | Maintenance Requests | ✅ |
| 7 | Work Order | ✅ |
| 8 | Work Order Activity | ✅ |
| 9 | Work Order Equipment & Labor | ✅ |
| 10 | Work Order Labor Assignment | ✅ |
| 11 | Parts Issue | ✅ |
| 12 | Parts Return | ✅ |
| 13 | Purchase Request | ✅ |
| 14 | Purchase Request Line | ✅ |
| 15 | Purchase Order | ✅ |
| 16 | State Machines (5 diagrams) | ✅ |

### 2.2 Infrastructure Profile

| Component | Current Configuration |
|-----------|----------------------|
| Frontend | Nuxt.js on port 3015, Node 20 |
| Backend | FastAPI/Uvicorn on port 8015 |
| Database | PostgreSQL (eam-chi) |
| Reverse Proxy | Nginx (HTTP only on port 80) |
| Real-time | Socket.IO |
| Deployment | Systemd services, single server |
| Environment | Cloned from eam-itba via shell script |

---

## 3. Gap Analysis — Infrastructure & Security

### 3.1 CRITICAL Gaps

| # | Gap | Current State | Required State | Risk | Recommendation |
|---|-----|---------------|----------------|------|----------------|
| S-1 | **Hardcoded Credentials** | Passwords, DB credentials, and secret keys are plaintext in `clone_to_chi.sh` | Secrets managed via vault or environment-only injection | **Critical** — Full compromise if script is exposed | Migrate to HashiCorp Vault, AWS Secrets Manager, or at minimum `.env` files excluded from version control |
| S-2 | **No SSL/TLS** | Nginx listens on port 80 only (HTTP) | HTTPS with TLS 1.2+ enforced, HSTS enabled | **Critical** — All traffic (including auth tokens) transmitted in cleartext | Deploy Let's Encrypt via Certbot; add `ssl_protocols TLSv1.2 TLSv1.3;` and HSTS header |
| S-3 | **No Security Headers** | Nginx config has no security headers | CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy | **High** — Vulnerable to clickjacking, MIME sniffing, XSS | Add security headers block to nginx server config |
| S-4 | **No Rate Limiting** | No request rate limiting on any endpoint | Rate limiting on API and auth endpoints | **High** — Susceptible to brute-force and DoS | Add `limit_req_zone` in nginx; implement application-level throttling on `/api/auth/` |
| S-5 | **No File Upload Limits** | No `client_max_body_size` in nginx | Configured upload size limits | **Medium** — Potential DoS via large file uploads | Set `client_max_body_size` to appropriate limit (e.g., 50M) |

### 3.2 HIGH Gaps

| # | Gap | Current State | Required State | Risk | Recommendation |
|---|-----|---------------|----------------|------|----------------|
| I-1 | **Single Server Deployment** | All services on one host | High availability with redundancy | **High** — Single point of failure | Implement load balancer + minimum 2 app servers; consider container orchestration |
| I-2 | **No Containerization** | Bare-metal systemd services | Docker/Kubernetes deployment | **Medium** — Inconsistent environments, hard to scale | Containerize with Docker Compose (minimum) or Kubernetes for production |
| I-3 | **No Database Backup Automation** | Manual pg_dump in clone script only | Automated daily backups with retention policy and tested restores | **High** — Data loss risk | Implement pg_basebackup or WAL archiving with automated schedule |
| I-4 | **No Monitoring/Alerting** | No evidence of monitoring stack | APM, uptime monitoring, error tracking, alerting | **High** — No visibility into system health or failures | Deploy Prometheus + Grafana or Datadog; add Sentry for error tracking |
| I-5 | **No CI/CD Pipeline** | Manual deployment via shell script | Automated build, test, deploy pipeline | **Medium** — Error-prone releases, no rollback capability | Implement GitHub Actions or GitLab CI with staging → production promotion |
| I-6 | **No Log Management** | Systemd journal logs only | Centralized logging with search and retention | **Medium** — Difficult to troubleshoot and audit | Deploy ELK stack or Loki + Grafana for centralized log aggregation |
| I-7 | **Missing `/uploads/` proxy in deployment** | Nginx in `clone_to_chi.sh` (Step 9) omits `/uploads/` route | `/uploads/` route proxied to backend (as in the standalone nginx config) | **Medium** — File uploads may not be served correctly after deployment | Add `/uploads/` location block to the nginx config in the deployment script |

---

## 4. Gap Analysis — Functional / EAM Modules

### 4.1 Missing Core EAM Modules

| # | Module | Industry Standard | Current State | Priority | Notes |
|---|--------|-------------------|---------------|----------|-------|
| F-1 | **Preventive Maintenance (PM) Scheduling** | Calendar-based and meter-based PM with auto WO generation | ❌ Not evident | **Critical** | Core EAM requirement — auto-generate WOs based on time or usage intervals |
| F-2 | **Condition-Based / Predictive Maintenance** | Condition monitoring, thresholds, predictive analytics | ❌ Not evident | **High** | Integrate sensor data / IoT for condition-based triggers |
| F-3 | **Asset Hierarchy & Location Tree** | Parent-child asset relationships, functional locations | ❓ Unknown (may exist within Asset Record) | **Critical** | Essential for cost rollup, failure propagation analysis |
| F-4 | **Failure Analysis (FMEA / RCA)** | Failure codes, cause codes, remedy codes, failure history | ❌ Not evident | **High** | Required for reliability engineering and ISO 14224 compliance |
| F-5 | **Depreciation & Asset Financials** | Straight-line, declining balance, cost tracking per asset | ❌ Not evident | **Medium** | Asset lifecycle costing, TCO analysis |
| F-6 | **Warranty Tracking** | Warranty periods, terms, claim management per asset | ❌ Not evident | **Medium** | Avoid unnecessary maintenance spend on warranted assets |
| F-7 | **Contract Management** | Service contracts, SLAs, vendor agreements | ❌ Not evident | **Medium** | Track service level agreements and contractor obligations |
| F-8 | **Vendor / Supplier Management** | Vendor registry, performance tracking, approved vendor lists | ❌ Not evident | **Medium** | Procurement optimization and vendor accountability |
| F-9 | **Reporting & Analytics Dashboard** | KPIs (MTBF, MTTR, OEE, backlog), charts, exportable reports | ❌ Not evident | **High** | Management visibility; decision-making support |
| F-10 | **Document Management** | Attach manuals, drawings, SOPs to assets and WOs | ❓ Unknown (uploads endpoint exists) | **Medium** | File attachments may partially exist via `/uploads/` |

### 4.2 Missing Supporting Features

| # | Feature | Current State | Priority | Notes |
|---|---------|---------------|----------|-------|
| F-11 | **Notification & Alerting System** | Socket.IO exists (real-time capable) | **High** | Email/SMS/push notifications for WO assignments, approvals, overdue tasks |
| F-12 | **Mobile / Offline Access** | Nuxt.js (web only) | **High** | Field technicians need mobile-friendly UI with offline data entry |
| F-13 | **Barcode / QR Code Scanning** | ❌ Not evident | **Medium** | Quick asset identification, inventory counting, parts issue |
| F-14 | **GIS / Location Mapping** | ❌ Not evident | **Low–Medium** | Useful for infrastructure-heavy or distributed asset portfolios |
| F-15 | **Audit Trail / Change Logging** | ❌ Not evident | **High** | Regulatory compliance; track who changed what, when |
| F-16 | **Role-Based Access Control (RBAC)** | ❓ Unknown | **Critical** | Multi-level permissions: admin, planner, technician, requester, viewer |
| F-17 | **Approval Workflows** | State machines exist (5 state diagrams) | **Medium** | Verify multi-level approvals are supported (e.g., PO > $10K needs manager) |
| F-18 | **Integration Layer (API/Webhooks)** | FastAPI backend (REST API exists) | **Medium** | ERP integration, SCADA/IoT feeds, accounting system sync |
| F-19 | **Safety / LOTO Procedures** | ❌ Not evident | **Medium** | Safety permits, lockout-tagout tracking for hazardous work |
| F-20 | **Energy Management** | ❌ Not evident | **Low** | Track energy consumption per asset/facility |
| F-21 | **Calibration Management** | ❌ Not evident | **Low–Medium** | Required in manufacturing and lab environments |
| F-22 | **Multi-Site / Multi-Organization** | Cloned as separate instance | **Medium** | Centralized multi-tenant architecture would be more efficient than per-site clones |

---

## 5. Gap Analysis — Deployment & Operations

| # | Gap | Current State | Required State | Priority |
|---|-----|---------------|----------------|----------|
| D-1 | **No Staging Environment** | Direct clone from ITBA to production | Staging → UAT → Production promotion | **High** |
| D-2 | **No Database Migration Strategy** | Schema from pg_dump of source | Version-controlled migrations (Alembic) | **High** |
| D-3 | **No Automated Testing** | No test suite visible | Unit, integration, and E2E test suites | **High** |
| D-4 | **No Disaster Recovery Plan** | No recovery procedures documented | Documented DR plan with RTO/RPO targets | **High** |
| D-5 | **No Configuration Management** | Hardcoded values in scripts | Infrastructure-as-code (Ansible, Terraform) | **Medium** |
| D-6 | **Instance Cloning Approach** | Separate full clone per organization | Shared multi-tenant platform or parameterized deployment | **Medium** |
| D-7 | **No Health Check Endpoints** | `curl` checks in deploy script only | `/health` and `/ready` endpoints with proper status checks | **Medium** |

---

## 6. Compliance Gaps

| Standard | Area | Status | Gap |
|----------|------|--------|-----|
| **ISO 55000** | Asset Management System | ⚠️ Partial | Missing lifecycle costing, risk-based decision frameworks, performance metrics |
| **ISO 14224** | Reliability & Maintenance Data | ❌ Not evident | No standardized failure/cause/mechanism taxonomy |
| **OSHA / Safety** | Safety Management | ❌ Not evident | No LOTO procedures, safety permit workflows |
| **SOC 2** | Security Controls | ❌ Not compliant | Hardcoded credentials, no encryption in transit, no audit logging |
| **GDPR / Data Privacy** | Personal Data Protection | ❓ Unknown | Need to assess PII handling in asset/labor records |

---

## 7. Priority Matrix

### Immediate (0–30 days)
1. **S-1** Remove hardcoded credentials; implement secrets management
2. **S-2** Enable HTTPS/TLS with Let's Encrypt
3. **S-3** Add nginx security headers
4. **S-4** Implement rate limiting
5. **I-7** Fix `/uploads/` proxy inconsistency in deployment script
6. **I-3** Implement automated database backups

### Short-Term (1–3 months)
7. **F-1** Implement Preventive Maintenance scheduling
8. **F-9** Build reporting & analytics dashboard
9. **F-16** Verify and harden RBAC implementation
10. **F-15** Implement comprehensive audit trail
11. **I-4** Deploy monitoring and alerting stack
12. **D-1** Establish staging environment
13. **D-3** Implement automated testing

### Medium-Term (3–6 months)
14. **F-2** Condition-based maintenance / IoT integration
15. **F-4** Failure analysis (FMEA/RCA) module
16. **F-11** Notification system (email/SMS/push)
17. **F-12** Mobile-responsive UI with offline capability
18. **I-2** Containerize with Docker
19. **I-5** Set up CI/CD pipeline
20. **F-7** Contract management module
21. **F-8** Vendor management module

### Long-Term (6–12 months)
22. **F-22** Multi-site / multi-tenant architecture
23. **F-5** Asset financial tracking & depreciation
24. **F-13** Barcode/QR scanning capability
25. **F-14** GIS/location mapping
26. **I-1** High availability deployment
27. **D-4** Documented disaster recovery plan

---

## 8. Risk Summary

| Risk Level | Count | Key Items |
|------------|-------|-----------|
| 🔴 **Critical** | 5 | Hardcoded secrets, no TLS, PM scheduling, asset hierarchy, RBAC |
| 🟠 **High** | 12 | Rate limiting, single-server, no backups, no monitoring, failure analysis, reporting, audit trail, notifications, mobile |
| 🟡 **Medium** | 13 | Upload limits, containerization, CI/CD, vendor mgmt, contracts, barcode, financial tracking, safety |
| 🟢 **Low** | 3 | Energy management, calibration, GIS mapping |

---

## 9. Conclusion

The CHI EAM system provides a functional baseline with core modules for asset records, work orders, inventory, procurement, and incident management. However, significant gaps exist in three critical areas:

1. **Security & Infrastructure** — Hardcoded credentials and lack of TLS encryption present immediate security risks that must be remediated before production use.
2. **Preventive Maintenance** — The absence of automated PM scheduling undermines the core value proposition of an EAM system.
3. **Operational Maturity** — No automated backups, monitoring, CI/CD, or testing creates operational risk.

Addressing the **Immediate** priority items will reduce the most critical risks. The **Short-Term** items will bring the system to a competitive EAM feature set. **Medium** and **Long-Term** items will mature the platform toward enterprise-grade reliability and capability.

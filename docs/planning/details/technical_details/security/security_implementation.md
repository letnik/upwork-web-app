# Безпека та комплайенс Upwork AI Assistant

> **Детальна документація по безпеці, приватності та регуляторному комплайенсу**

---

## Зміст

1. [Безпека даних](#безпека-даних)
2. [GDPR/CCPA комплайенс](#gdprccpa-комплайенс)
3. [Аутентифікація та авторизація](#аутентифікація-та-авторизація)
4. [Шифрування](#шифрування)
5. [Моніторинг безпеки](#моніторинг-безпеки)
6. [Інфраструктурна безпека](#інфраструктурна-безпека)
7. [Тестування безпеки](#тестування-безпеки)

---

## Безпека даних

### **Data Classification**

#### **Категорії даних**
1. **Персональні дані (PII)**
   - Email адреси
   - Імена та прізвища
   - Номери телефонів
   - IP адреси

2. **Чутливі дані**
   - API ключі користувачів
   - Паролі (хешовані)
   - Токени доступу
   - Фінансова інформація

3. **Бізнес дані**
   - Вакансії та пропозиції
   - Аналітичні дані
   - Використання AI
   - Метрики продуктивності

### **Data Protection Measures**

#### **Шифрування даних**
```python
class DataEncryption:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        self.cipher = AES.new(self.key, AES.MODE_GCM)
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data at rest"""
        ciphertext, tag = self.cipher.encrypt_and_digest(data.encode())
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode(),
            "nonce": base64.b64encode(self.cipher.nonce).decode()
        }
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        tag = base64.b64decode(encrypted_data["tag"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

#### **Data Access Control**
```python
class DataAccessControl:
    def __init__(self):
        self.db = Database()
        self.audit_logger = AuditLogger()
    
    async def check_user_permission(self, user_id, resource_type, resource_id):
        """Check if user has permission to access resource"""
        permissions = await self.db.get_user_permissions(user_id)
        
        if resource_type == "job":
            return await self._check_job_permission(user_id, resource_id, permissions)
        elif resource_type == "proposal":
            return await self._check_proposal_permission(user_id, resource_id, permissions)
        
        return False
    
    async def log_data_access(self, user_id, resource_type, resource_id, action):
        """Log all data access for audit"""
        await self.audit_logger.log_access(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            timestamp=datetime.utcnow(),
            ip_address=request.client.host
        )
```

### **Data Retention Policy**

#### **Терміни зберігання**
```python
DATA_RETENTION_POLICY = {
    "user_data": {
        "active_users": "2 роки",
        "inactive_users": "6 місяців",
        "deleted_users": "30 днів"
    },
    "job_data": {
        "active_jobs": "1 рік",
        "expired_jobs": "6 місяців",
        "archived_jobs": "3 роки"
    },
    "proposal_data": {
        "active_proposals": "2 роки",
        "accepted_proposals": "5 років",
        "rejected_proposals": "1 рік"
    },
    "ai_generations": {
        "user_generations": "2 роки",
        "analytics_data": "3 роки",
        "training_data": "5 років"
    },
    "logs": {
        "application_logs": "1 рік",
        "security_logs": "3 роки",
        "audit_logs": "7 років"
    }
}
```

#### **Автоматичне очищення**
```python
class DataRetentionManager:
    async def cleanup_expired_data(self):
        """Automatically cleanup expired data"""
# Cleanup inactive users
        await self._cleanup_inactive_users()
        
# Cleanup expired jobs
        await self._cleanup_expired_jobs()
        
# Cleanup old AI generations
        await self._cleanup_old_ai_generations()
        
# Cleanup old logs
        await self._cleanup_old_logs()
    
    async def _cleanup_inactive_users(self):
        """Cleanup users inactive for 6 months"""
        cutoff_date = datetime.utcnow() - timedelta(days=180)
        
        inactive_users = await self.db.get_inactive_users(cutoff_date)
        
        for user in inactive_users:
            await self._anonymize_user_data(user.id)
            await self.db.delete_user(user.id)
```

---

## GDPR/CCPA комплайенс

### **Privacy by Design**

#### **Принципи приватності**
1. **Data Minimization** - збираємо тільки необхідні дані
2. **Purpose Limitation** - використовуємо дані тільки для заявлених цілей
3. **Storage Limitation** - зберігаємо дані тільки необхідний час
4. **Accuracy** - забезпечуємо точність даних
5. **Security** - захищаємо дані від несанкціонованого доступу
6. **Accountability** - несемо відповідальність за обробку даних

#### **Privacy Impact Assessment**
```python
class PrivacyImpactAssessment:
    def assess_data_processing(self, processing_activity):
        """Assess privacy impact of data processing"""
        risk_factors = {
            "data_volume": self._assess_data_volume(processing_activity),
            "data_sensitivity": self._assess_data_sensitivity(processing_activity),
            "processing_purpose": self._assess_processing_purpose(processing_activity),
            "data_sharing": self._assess_data_sharing(processing_activity),
            "retention_period": self._assess_retention_period(processing_activity)
        }
        
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        return {
            "risk_level": overall_risk,
            "risk_factors": risk_factors,
            "mitigation_measures": self._get_mitigation_measures(overall_risk)
        }
```

### **User Rights Implementation**

#### **Право на доступ**
```python
class UserRightsService:
    async def export_user_data(self, user_id):
        """Export all user data (GDPR Article 15)"""
        user_data = await self.db.get_user_data(user_id)
        
        export_data = {
            "personal_info": {
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "created_at": user_data.created_at,
                "last_login": user_data.last_login
            },
            "jobs": await self.db.get_user_jobs(user_id),
            "proposals": await self.db.get_user_proposals(user_id),
            "ai_generations": await self.db.get_user_ai_generations(user_id),
            "analytics": await self.db.get_user_analytics(user_id),
            "preferences": await self.db.get_user_preferences(user_id)
        }
        
        return export_data
```

#### **Право на забуття**
```python
    async def delete_user_data(self, user_id):
        """Delete user data (GDPR Article 17)"""
# Anonymize personal data
        await self._anonymize_user_data(user_id)
        
# Delete user account
        await self.db.delete_user(user_id)
        
# Delete associated data
        await self.db.delete_user_jobs(user_id)
        await self.db.delete_user_proposals(user_id)
        await self.db.delete_user_ai_generations(user_id)
        
# Log deletion for audit
        await self.audit_logger.log_data_deletion(user_id)
    
    async def _anonymize_user_data(self, user_id):
        """Anonymize user data instead of deletion"""
        anonymized_data = {
            "email": f"deleted_{user_id}@example.com",
            "first_name": "Deleted",
            "last_name": "User",
            "upwork_user_id": None
        }
        
        await self.db.update_user(user_id, anonymized_data)
```

#### **Право на виправлення**
```python
    async def update_user_data(self, user_id, updated_data):
        """Update user data (GDPR Article 16)"""
# Validate data
        validated_data = await self._validate_user_data(updated_data)
        
# Update user data
        await self.db.update_user(user_id, validated_data)
        
# Log update for audit
        await self.audit_logger.log_data_update(user_id, updated_data)
        
        return {"success": True, "message": "Data updated successfully"}
```

### **Consent Management**

#### **Управління згодою**
```python
class ConsentManager:
    async def record_consent(self, user_id, consent_type, consent_data):
        """Record user consent"""
        consent_record = {
            "user_id": user_id,
            "consent_type": consent_type,
            "consent_data": consent_data,
            "timestamp": datetime.utcnow(),
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
        
        await self.db.save_consent(consent_record)
    
    async def check_consent(self, user_id, consent_type):
        """Check if user has given consent"""
        consent = await self.db.get_user_consent(user_id, consent_type)
        
        if not consent:
            return False
        
# Check if consent is still valid
        if consent.expires_at and consent.expires_at < datetime.utcnow():
            return False
        
        return True
    
    async def withdraw_consent(self, user_id, consent_type):
        """Withdraw user consent"""
        await self.db.withdraw_consent(user_id, consent_type)
        
# Stop processing data that requires this consent
        await self._stop_data_processing(user_id, consent_type)
```

---

## Аутентифікація та авторизація

### **Multi-Factor Authentication**

#### **MFA Implementation**
```python
class MFAService:
    def __init__(self):
        self.totp = pyotp.TOTP
        self.email_service = EmailService()
    
    async def setup_mfa(self, user_id):
        """Setup MFA for user"""
# Generate secret key
        secret = pyotp.random_base32()
        
# Generate QR code
        qr_code = pyotp.totp.TOTP(secret).provisioning_uri(
            name=f"user_{user_id}",
            issuer_name="Upwork AI Assistant"
        )
        
# Save secret (encrypted)
        encrypted_secret = self.encryption.encrypt(secret)
        await self.db.save_mfa_secret(user_id, encrypted_secret)
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": self._generate_backup_codes()
        }
    
    async def verify_mfa(self, user_id, token):
        """Verify MFA token"""
# Get user's MFA secret
        encrypted_secret = await self.db.get_mfa_secret(user_id)
        secret = self.encryption.decrypt(encrypted_secret)
        
# Verify token
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    def _generate_backup_codes(self):
        """Generate backup codes for MFA"""
        codes = []
        for _ in range(10):
            code = ''.join(random.choices('0123456789', k=8))
            codes.append(code)
        return codes
```

### **JWT Token Management**

#### **Token Configuration**
```python
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "issuer": "upwork-ai-assistant",
    "audience": "upwork-ai-users"
}

class JWTService:
    def __init__(self):
        self.secret_key = JWT_CONFIG["secret_key"]
        self.algorithm = JWT_CONFIG["algorithm"]
    
    def create_access_token(self, user_id, permissions):
        """Create JWT access token"""
        payload = {
            "sub": str(user_id),
            "permissions": permissions,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=JWT_CONFIG["access_token_expire_minutes"]),
            "iss": JWT_CONFIG["issuer"],
            "aud": JWT_CONFIG["audience"]
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id):
        """Create JWT refresh token"""
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=JWT_CONFIG["refresh_token_expire_days"]),
            "iss": JWT_CONFIG["issuer"],
            "aud": JWT_CONFIG["audience"]
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                issuer=JWT_CONFIG["issuer"],
                audience=JWT_CONFIG["audience"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

### **Role-Based Access Control**

#### **RBAC Implementation**
```python
class RBACService:
    def __init__(self):
        self.db = Database()
    
    async def check_permission(self, user_id, resource, action):
        """Check if user has permission for action on resource"""
        user_roles = await self.db.get_user_roles(user_id)
        
        for role in user_roles:
            permissions = await self.db.get_role_permissions(role.id)
            
            for permission in permissions:
                if (permission.resource == resource and 
                    permission.action == action):
                    return True
        
        return False
    
    async def assign_role(self, user_id, role_name):
        """Assign role to user"""
        role = await self.db.get_role_by_name(role_name)
        if not role:
            raise ValueError(f"Role {role_name} not found")
        
        await self.db.assign_user_role(user_id, role.id)
    
    async def create_role(self, role_name, permissions):
        """Create new role with permissions"""
        role_id = await self.db.create_role(role_name)
        
        for permission in permissions:
            await self.db.add_role_permission(role_id, permission)
        
        return role_id
```

---

## Шифрування

### **Encryption at Rest**

#### **Database Encryption**
```sql
-- Enable encryption for PostgreSQL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Encrypt sensitive columns
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt API keys
ALTER TABLE user_api_keys 
ADD COLUMN api_key_encrypted BYTEA;

-- Function to encrypt API key
CREATE OR REPLACE FUNCTION encrypt_api_key(api_key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(api_key, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;

-- Function to decrypt API key
CREATE OR REPLACE FUNCTION decrypt_api_key(encrypted_key BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_key, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;
```

#### **File Storage Encryption**
```python
class FileEncryption:
    def __init__(self):
        self.key = os.getenv("FILE_ENCRYPTION_KEY")
    
    def encrypt_file(self, file_path):
        """Encrypt file before storing"""
        with open(file_path, 'rb') as file:
            data = file.read()
        
# Generate random IV
        iv = os.urandom(16)
        
# Encrypt data
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = self._pad(data)
        encrypted_data = cipher.encrypt(padded_data)
        
# Store encrypted file
        encrypted_path = file_path + '.enc'
        with open(encrypted_path, 'wb') as file:
            file.write(iv + encrypted_data)
        
        return encrypted_path
    
    def decrypt_file(self, encrypted_path):
        """Decrypt file for reading"""
        with open(encrypted_path, 'rb') as file:
            data = file.read()
        
# Extract IV and encrypted data
        iv = data[:16]
        encrypted_data = data[16:]
        
# Decrypt data
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        return self._unpad(decrypted_data)
```

### **Encryption in Transit**

#### **TLS Configuration**
```python
# TLS configuration for FastAPI
TLS_CONFIG = {
    "certfile": "/path/to/cert.pem",
    "keyfile": "/path/to/key.pem",
    "ssl_version": ssl.PROTOCOL_TLSv1_3,
    "ciphers": "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256",
    "verify_mode": ssl.CERT_REQUIRED
}

# HTTPS middleware
class HTTPSMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
# Force HTTPS
            if scope.get("scheme") != "https":
                return await self._redirect_to_https(scope, receive, send)
        
        await self.app(scope, receive, send)
    
    async def _redirect_to_https(self, scope, receive, send):
        """Redirect HTTP to HTTPS"""
        response = {
            "type": "http.response.start",
            "status": 301,
            "headers": [
                (b"location", b"https://" + scope["headers"][b"host"] + scope["path"].encode())
            ]
        }
        await send(response)
```

---

## Моніторинг безпеки

### **Security Event Monitoring**

#### **Security Logging**
```python
class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.alert_service = AlertService()
    
    async def log_security_event(self, event_type, user_id, details):
        """Log security event"""
        log_entry = {
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "details": details
        }
        
# Log to security log
        self.logger.warning(f"Security event: {log_entry}")
        
# Store in database
        await self.db.save_security_event(log_entry)
        
# Check for suspicious patterns
        await self._check_suspicious_activity(user_id, event_type)
    
    async def _check_suspicious_activity(self, user_id, event_type):
        """Check for suspicious activity patterns"""
        recent_events = await self.db.get_recent_security_events(user_id, hours=1)
        
# Check for multiple failed logins
        failed_logins = [e for e in recent_events if e["event_type"] == "failed_login"]
        if len(failed_logins) > 5:
            await self._trigger_security_alert("multiple_failed_logins", user_id)
        
# Check for unusual access patterns
        if await self._is_unusual_access(user_id):
            await self._trigger_security_alert("unusual_access", user_id)
```

#### **Security Alerts**
```python
class SecurityAlertService:
    async def trigger_alert(self, alert_type, user_id, details):
        """Trigger security alert"""
        alert = {
            "type": alert_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "details": details,
            "severity": self._get_alert_severity(alert_type)
        }
        
# Store alert
        await self.db.save_security_alert(alert)
        
# Send notifications
        await self._send_alert_notifications(alert)
        
# Take automated actions
        await self._take_automated_actions(alert)
    
    async def _send_alert_notifications(self, alert):
        """Send alert notifications"""
        if alert["severity"] == "high":
# Send immediate notification
            await self.email_service.send_security_alert(alert)
            await self.slack_service.send_security_alert(alert)
        
# Log to monitoring system
        await self.monitoring_service.log_security_alert(alert)
    
    async def _take_automated_actions(self, alert):
        """Take automated security actions"""
        if alert["type"] == "multiple_failed_logins":
# Temporarily block user
            await self.auth_service.temporarily_block_user(alert["user_id"])
        
        elif alert["type"] == "suspicious_activity":
# Require additional verification
            await self.auth_service.require_additional_verification(alert["user_id"])
```

### **Vulnerability Scanning**

#### **Automated Security Scanning**
```python
class SecurityScanner:
    def __init__(self):
        self.dependency_scanner = DependencyScanner()
        self.code_scanner = CodeScanner()
        self.container_scanner = ContainerScanner()
    
    async def run_security_scan(self):
        """Run comprehensive security scan"""
        results = {
            "dependencies": await self._scan_dependencies(),
            "code": await self._scan_code(),
            "containers": await self._scan_containers(),
            "infrastructure": await self._scan_infrastructure()
        }
        
# Generate report
        report = await self._generate_security_report(results)
        
# Send alerts for critical issues
        await self._alert_critical_issues(results)
        
        return report
    
    async def _scan_dependencies(self):
        """Scan for vulnerable dependencies"""
        return await self.dependency_scanner.scan()
    
    async def _scan_code(self):
        """Scan code for security issues"""
        return await self.code_scanner.scan()
    
    async def _scan_containers(self):
        """Scan containers for vulnerabilities"""
        return await self.container_scanner.scan()
```

---

## Інфраструктурна безпека

### **Network Security**

#### **VPC Configuration**
```yaml
# AWS VPC configuration
VPC:
  CIDR: 10.0.0.0/16
  Subnets:
    - Public: 10.0.1.0/24
    - Private: 10.0.2.0/24
    - Database: 10.0.3.0/24
  
  Security Groups:
    - WebServer:
        - Inbound: 80, 443 (HTTP/HTTPS)
        - Outbound: All
    - Application:
        - Inbound: 8000 (from WebServer)
        - Outbound: Database, Redis
    - Database:
        - Inbound: 5432 (from Application)
        - Outbound: None
```

#### **Firewall Rules**
```python
class FirewallManager:
    def __init__(self):
        self.aws_client = boto3.client('ec2')
    
    async def update_security_groups(self):
        """Update security group rules"""
# Allow only necessary ports
        rules = [
            {"port": 80, "source": "0.0.0.0/0"},   # HTTP
            {"port": 443, "source": "0.0.0.0/0"},  # HTTPS
            {"port": 22, "source": "10.0.0.0/8"},  # SSH (internal only)
        ]
        
        for rule in rules:
            await self._add_security_group_rule(rule)
    
    async def block_suspicious_ips(self, ip_list):
        """Block suspicious IP addresses"""
        for ip in ip_list:
            await self._add_block_rule(ip)
```

### **Access Control**

#### **SSH Key Management**
```python
class SSHKeyManager:
    def __init__(self):
        self.aws_client = boto3.client('ec2')
    
    async def rotate_ssh_keys(self):
        """Rotate SSH keys regularly"""
# Generate new key pair
        new_key = await self._generate_key_pair()
        
# Update instances
        instances = await self._get_all_instances()
        for instance in instances:
            await self._update_instance_key(instance, new_key)
        
# Remove old keys
        await self._remove_old_keys()
    
    async def _generate_key_pair(self):
        """Generate new SSH key pair"""
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        
        return {
            "private_key": key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            "public_key": key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        }
```

---

## 🧪 Тестування безпеки

### **Security Testing Strategy**

#### **Penetration Testing**
```python
class SecurityTester:
    def __init__(self):
        self.pentest_tools = {
            "nmap": NmapScanner(),
            "sqlmap": SQLMapScanner(),
            "burp": BurpScanner(),
            "zap": OWASPZapScanner()
        }
    
    async def run_penetration_test(self):
        """Run comprehensive penetration test"""
        results = {
            "network_scan": await self._run_network_scan(),
            "web_application_scan": await self._run_web_scan(),
            "api_security_test": await self._run_api_security_test(),
            "authentication_test": await self._run_auth_test(),
            "authorization_test": await self._run_authz_test()
        }
        
# Generate report
        report = await self._generate_penetration_report(results)
        
# Fix critical issues
        await self._fix_critical_issues(results)
        
        return report
    
    async def _run_network_scan(self):
        """Run network security scan"""
        return await self.pentest_tools["nmap"].scan()
    
    async def _run_web_scan(self):
        """Run web application security scan"""
        return await self.pentest_tools["zap"].scan()
    
    async def _run_api_security_test(self):
        """Test API security"""
        test_cases = [
            "authentication_bypass",
            "authorization_bypass",
            "input_validation",
            "sql_injection",
            "xss_attack"
        ]
        
        results = {}
        for test_case in test_cases:
            results[test_case] = await self._run_api_test(test_case)
        
        return results
```

#### **Automated Security Testing**
```python
class AutomatedSecurityTester:
    async def run_security_tests(self):
        """Run automated security tests"""
        tests = [
            self._test_authentication(),
            self._test_authorization(),
            self._test_input_validation(),
            self._test_sql_injection(),
            self._test_xss_protection(),
            self._test_csrf_protection()
        ]
        
        results = await asyncio.gather(*tests)
        
# Generate test report
        report = self._generate_test_report(results)
        
# Fail build if critical issues found
        if self._has_critical_issues(results):
            raise SecurityTestFailed("Critical security issues found")
        
        return report
    
    async def _test_authentication(self):
        """Test authentication security"""
        test_cases = [
            {"username": "admin", "password": "wrong"},
            {"username": "nonexistent", "password": "any"},
            {"username": "", "password": ""},
            {"username": "admin'--", "password": "any"}
        ]
        
        results = []
        for test_case in test_cases:
            result = await self._test_login(test_case)
            results.append(result)
        
        return results
```

---

**Статус**: Створено на основі всіх готових відповідей  
**Пріоритет**: Критичний  
**Останнє оновлення**: 2024-12-19 19:30 
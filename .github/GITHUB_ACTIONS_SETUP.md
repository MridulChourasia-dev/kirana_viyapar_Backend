# GitHub Actions Secrets Setup Guide

This guide explains how to configure all necessary secrets for the CI/CD pipelines to work correctly.

## Prerequisites

- GitHub repository with admin access
- AWS account with programmatic access (IAM user)
- Docker Hub account
- Google Play Console account (for Android releases)

## Step-by-Step Setup

### 1. AWS Credentials

These credentials are used for deploying to ECS and managing AWS resources.

1. Go to **AWS IAM Console** → **Users** → Create a new user or select existing
2. Create an **Access Key** (IAM → Users → Security Credentials → Access Keys)
3. Copy the **Access Key ID** and **Secret Access Key**
4. In GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:
- **Name:** `AWS_ACCESS_KEY_ID`
  **Value:** Your AWS access key ID
- **Name:** `AWS_SECRET_ACCESS_KEY`
  **Value:** Your AWS secret access key
- **Name:** `AWS_REGION`
  **Value:** `us-east-1` (or your region)

**IAM Policy Required:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Docker Hub Credentials

Used for building and pushing Docker images.

1. Go to **Docker Hub** → **Account Settings** → **Security**
2. Create an **Access Token** (Save the token securely)
3. In GitHub: Add these secrets:
   - **Name:** `DOCKER_USERNAME`
     **Value:** Your Docker Hub username
   - **Name:** `DOCKER_PASSWORD`
     **Value:** The access token from Docker Hub

### 3. ECS Deployment Configuration

Used by the backend CI/CD pipeline.

1. From your Terraform outputs, get the cluster and service names
2. In GitHub: Add these secrets:
   - **Name:** `ECS_CLUSTER_NAME`
     **Value:** `viyapar-prod` (from terraform.tf)
   - **Name:** `ECS_SERVICE_NAME`
     **Value:** `viyapar-backend` (from alb_ecs_service.tf)

### 4. Google Play Console Credentials (for Android)

Used for uploading builds to Google Play Store.

1. Go to **Google Play Console** → **All applications** → Your app
2. **Setup** → **API access** → **Service Accounts**
3. Create or select a service account
4. Generate a **JSON key** and download it
5. In GitHub: Add these secrets:
   - **Name:** `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`
     **Value:** The entire JSON file contents
   - **Name:** `GOOGLE_PLAY_APP_ID`
     **Value:** Your app ID (e.g., `com.viyapar.mobile`)

### 5. Expo/EAS Configuration (for Mobile Builds)

Used for building iOS and Android apps through Expo.

1. Go to **Expo.dev** → **Account Settings** → **Access Tokens**
2. Create a new token (Save it securely)
3. In GitHub: Add these secrets:
   - **Name:** `EAS_TOKEN`
     **Value:** Your Expo access token
   - **Name:** `EXPO_EMAIL`
     **Value:** Your Expo account email

### 6. Optional: Slack Notifications

For deployment notifications.

1. Create a Slack app: **api.slack.com** → **Your Apps** → **Create New App**
2. Enable **Incoming Webhooks**
3. Create a webhook for your channel
4. In GitHub: Add these secrets:
   - **Name:** `SLACK_WEBHOOK_URL`
     **Value:** The webhook URL

### 7. Code Signing Certificates (Optional but Recommended)

For signing Android APK/AAB files.

1. Generate a **signing key** (Android):
   ```bash
   keytool -genkey -v -keystore keystore.jks \
     -keyalg RSA -keysize 2048 -validity 10000 \
     -alias viyapar_key
   ```

2. Encode the keystore file:
   ```bash
   base64 keystore.jks | tr -d '\n' > keystore_base64.txt
   ```

3. In GitHub: Add these secrets:
   - **Name:** `ANDROID_KEYSTORE_BASE64`
     **Value:** Contents of `keystore_base64.txt`
   - **Name:** `ANDROID_KEYSTORE_PASSWORD`
     **Value:** Your keystore password
   - **Name:** `ANDROID_KEY_ALIAS`
     **Value:** `viyapar_key`
   - **Name:** `ANDROID_KEY_PASSWORD`
     **Value:** Your key password

## Verification Checklist

After adding all secrets, verify in GitHub:

```bash
# From your repository
Settings → Secrets and variables → Actions

# Should see these repository secrets:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- DOCKER_USERNAME
- DOCKER_PASSWORD
- ECS_CLUSTER_NAME
- ECS_SERVICE_NAME
- GOOGLE_PLAY_SERVICE_ACCOUNT_JSON
- GOOGLE_PLAY_APP_ID
- EAS_TOKEN
- EXPO_EMAIL
- SLACK_WEBHOOK_URL (optional)
- ANDROID_KEYSTORE_BASE64 (optional)
- ANDROID_KEYSTORE_PASSWORD (optional)
- ANDROID_KEY_ALIAS (optional)
- ANDROID_KEY_PASSWORD (optional)
```

## Secrets Management Best Practices

1. **Rotation Schedule**
   - Rotate AWS credentials every 90 days
   - Rotate Docker Hub tokens every 6 months
   - Rotate signing certificates every 2 years

2. **Access Control**
   - Limit secret access to necessary workflows
   - Use environment-specific secrets (dev vs prod)
   - Review GitHub Actions logs regularly

3. **Document Changes**
   - Keep a log of when secrets were rotated
   - Note which secrets are used in which workflows
   - Store backup copies securely (e.g., AWS Secrets Manager)

4. **Security Alerts**
   - Enable GitHub Security Advisories
   - Monitor for exposed secrets in commits
   - Enable branch protection rules

## Troubleshooting

### "Repository secret not found" error

**Solution:**
1. Verify the secret name matches exactly (case-sensitive)
2. Ensure you're using `secrets.SECRET_NAME` in workflow YAML
3. Check that secrets are available in the current branch

### AWS Deployment Fails

**Solution:**
1. Verify AWS credentials are correct
2. Check IAM policy includes required permissions
3. Ensure ECS cluster and service names match
4. Verify ECS task definition revision is updated

### Docker Push Fails

**Solution:**
1. Verify Docker Hub credentials are correct
2. Check repository is public or you have push permission
3. Ensure image name matches the repository
4. Check Docker Hub token hasn't expired

### Play Store Upload Fails

**Solution:**
1. Verify service account has "Releases Editor" role in Play Console
2. Check JSON key is valid and hasn't expired
3. Ensure app is set up in Play Console
4. Verify app bundle format is correct (AAB)

## Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Docker Hub Token Documentation](https://docs.docker.com/docker-hub/access-tokens/)
- [Google Play Console API](https://developers.google.com/android-publisher)
- [Expo CLI Documentation](https://docs.expo.dev/more/expo-cli/)

## Next Steps

1. ✅ Add all required secrets to GitHub
2. Push a test commit to trigger workflows
3. Monitor workflow execution in GitHub Actions
4. Verify deployment in AWS ECS and Play Store
5. Set up monitoring and alerts

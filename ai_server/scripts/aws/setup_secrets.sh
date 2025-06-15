#!/bin/bash

# AWS에 AIStudios API 키를 Secrets Manager에 저장하는 스크립트

set -e

echo "🔐 AWS Secrets Manager에 AIStudios API 키 설정"
echo "================================================"

# API 키 입력 받기
read -p "AIStudios API 키를 입력하세요: " -s API_KEY
echo

if [ -z "$API_KEY" ]; then
    echo "❌ API 키가 입력되지 않았습니다."
    exit 1
fi

# AWS 리전 설정 (기본값: ap-northeast-2)
AWS_REGION=${AWS_DEFAULT_REGION:-ap-northeast-2}
echo "📍 AWS 리전: $AWS_REGION"

# 시크릿 데이터 준비
SECRET_DATA=$(cat <<EOF
{
  "AISTUDIOS_API_KEY": "$API_KEY",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "production"
}
EOF
)

echo "🔄 Secrets Manager에 시크릿 생성 중..."

# 시크릿 생성 또는 업데이트
SECRET_NAME="veriview/aistudios"

# 기존 시크릿이 있는지 확인
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "📝 기존 시크릿 업데이트 중..."
    aws secretsmanager update-secret \
        --secret-id "$SECRET_NAME" \
        --secret-string "$SECRET_DATA" \
        --region "$AWS_REGION"
else
    echo "🆕 새 시크릿 생성 중..."
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "VeriView AIStudios API Keys for Production" \
        --secret-string "$SECRET_DATA" \
        --region "$AWS_REGION"
fi

echo "✅ 시크릿 설정 완료: $SECRET_NAME"

# 추가 시크릿 생성 (다른 이름으로도 접근 가능하도록)
ADDITIONAL_SECRET_NAME="ai-server/api-keys"

echo "🔄 추가 시크릿 생성 중: $ADDITIONAL_SECRET_NAME"

if aws secretsmanager describe-secret --secret-id "$ADDITIONAL_SECRET_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    aws secretsmanager update-secret \
        --secret-id "$ADDITIONAL_SECRET_NAME" \
        --secret-string "$SECRET_DATA" \
        --region "$AWS_REGION"
else
    aws secretsmanager create-secret \
        --name "$ADDITIONAL_SECRET_NAME" \
        --description "VeriView AI Server API Keys" \
        --secret-string "$SECRET_DATA" \
        --region "$AWS_REGION"
fi

echo "✅ 모든 시크릿 설정 완료!"
echo ""
echo "📋 생성된 시크릿들:"
echo "  - $SECRET_NAME"
echo "  - $ADDITIONAL_SECRET_NAME"
echo ""
echo "🚀 이제 AWS에서 VeriView AI 서버를 시작할 수 있습니다:"
echo "  python run.py --mode main"
echo ""
echo "🔍 시크릿 확인:"
echo "  aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $AWS_REGION"

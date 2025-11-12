import json
import os
import uuid
import boto3

# Configuração do AWS
# Em um ambiente real, o nome da fila seria uma variável de ambiente
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "URL_DA_SUA_FILA_SQS")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME", "NOME_DO_SEU_BUCKET_S3")

sqs_client = boto3.client('sqs')
s3_client = boto3.client('s3')

def handler(event, context):
    """
    Função Lambda IniciarAvaliacao.
    Recebe a requisição do API Gateway, gera um ID de avaliação,
    cria URLs pré-assinadas para upload no S3 e envia a mensagem para o SQS.
    """
    try:
        # 1. Processar a entrada (simulando dados do celular e do usuário)
        # Em um ambiente real, a entrada viria do corpo da requisição HTTP
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        device_model = body.get('device_model')

        if not user_id or not device_model:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'user_id e device_model são obrigatórios'})
            }

        # 2. Gerar ID de Avaliação
        evaluation_id = str(uuid.uuid4())

        # 3. Gerar URLs pré-assinadas para upload de fotos no S3
        # O usuário precisará de URLs para enviar as fotos do aparelho
        s3_key = f"uploads/{user_id}/{evaluation_id}/"
        
        # Simulação de geração de URLs para 3 fotos
        presigned_urls = {}
        for i in range(1, 4):
            file_key = f"{s3_key}photo_{i}.jpg"
            presigned_url = s3_client.generate_presigned_post(
                Bucket=s3_bucket_name,
                Key=file_key,
                ExpiresIn=3600 # 1 hora de validade
            )
            presigned_urls[f'photo_{i}'] = presigned_url

        # 4. Enviar mensagem para a FilaAvaliacao (SQS)
        # A mensagem será processada pela Lambda ProcessaAvaliacao
        sqs_message = {
            'evaluation_id': evaluation_id,
            'user_id': user_id,
            'device_model': device_model,
            's3_key_prefix': s3_key,
            'status': 'PENDING_UPLOAD'
        }

        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(sqs_message)
        )

        # 5. Retornar resposta ao usuário
        return {
            'statusCode': 200,
            'body': json.dumps({
                'evaluation_id': evaluation_id,
                'message': 'Avaliação iniciada. Use as URLs para upload das fotos.',
                'upload_urls': presigned_urls
            })
        }

    except Exception as e:
        print(f"Erro ao iniciar avaliação: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Erro interno ao iniciar avaliação'})
        }
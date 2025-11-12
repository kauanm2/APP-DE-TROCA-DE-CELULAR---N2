import json
import os
import random
import boto3

# Configuração do AWS
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "DadosAparelhos")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def handler(event, context):
    """
    Função Lambda ProcessaAvaliacao.
    Consome a mensagem do SQS, simula a avaliação do aparelho (nota, condição, valor)
    e salva o laudo no DynamoDB.
    """
    try:
        # 1. Processar as mensagens do SQS
        for record in event['Records']:
            message_body = json.loads(record['body'])
            
            evaluation_id = message_body['evaluation_id']
            user_id = message_body['user_id']
            device_model = message_body['device_model']
            s3_key_prefix = message_body['s3_key_prefix']
            
            print(f"Processando avaliação ID: {evaluation_id} para o usuário: {user_id}")

            # 2. Simulação da Lógica de Avaliação
            # Em um ambiente real, esta etapa envolveria:
            # - Download das fotos do S3 (usando s3_key_prefix)
            # - Execução de modelos de Machine Learning para análise de danos
            # - Cálculo da nota (0 a 10) e valor de troca
            
            # Simulação de resultados
            nota = random.randint(5, 10)
            condicao = "Excelente" if nota >= 9 else "Boa" if nota >= 7 else "Regular"
            valor_troca = round(random.uniform(500.00, 3000.00), 2)
            
            # 3. Salvar o Laudo no DynamoDB
            table.put_item(
                Item={
                    'evaluation_id': evaluation_id,
                    'user_id': user_id,
                    'device_model': device_model,
                    'nota': nota,
                    'condicao': condicao,
                    'valor_troca': valor_troca,
                    'status': 'LAUDO_CONCLUIDO'
                }
            )
            
            print(f"Laudo ID {evaluation_id} salvo. Valor de troca: R$ {valor_troca}")

            # 4. Chamar a próxima função (SugereTroca)
            # Em um fluxo serverless, isso seria feito por um evento (ex: DynamoDB Stream, SNS, ou Step Functions)
            # Aqui, vamos simular a chamada direta para simplificar o exemplo, mas o ideal é usar eventos.
            # No nosso serverless.yml, vamos configurar o DynamoDB Stream para acionar a SugereTroca.
            # Para o código Python, vamos apenas retornar o resultado para o log.
            
            # O Step Functions seria o ideal para orquestrar F -> H -> L
            # Como estamos simulando Lambdas isoladas, o DynamoDB Stream é a melhor opção para acionar a SugereTroca.
            
        return {'statusCode': 200, 'body': 'Avaliações processadas com sucesso'}

    except Exception as e:
        print(f"Erro ao processar avaliação: {e}")
        # Em um ambiente real, a mensagem do SQS seria movida para uma Dead Letter Queue (DLQ)
        raise e
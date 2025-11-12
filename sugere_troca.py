import json
import os
import random
import boto3

# Configuração do AWS
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "DadosAparelhos")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "ARN_DO_SEU_TOPICO_SNS")

dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

# Simulação de um estoque de modelos ligeiramente melhores
ESTOQUE_MODELOS = [
    {"modelo": "iPhone 13 Pro", "valor_mercado": 5500.00, "ganhos": "Câmera Pro, Chip A15 Bionic"},
    {"modelo": "Samsung Galaxy S22", "valor_mercado": 4800.00, "ganhos": "Tela Dynamic AMOLED, Bateria de longa duração"},
    {"modelo": "Xiaomi 12", "valor_mercado": 3500.00, "ganhos": "Carregamento ultra-rápido, Desempenho em jogos"}
]

def handler(event, context):
    """
    Função Lambda SugereTroca.
    Acionada por um evento de stream do DynamoDB (quando um laudo é concluído).
    Busca sugestões de troca e envia uma notificação ao usuário.
    """
    try:
        # 1. Processar o evento do DynamoDB Stream
        for record in event['Records']:
            if record['eventName'] == 'INSERT' or record['eventName'] == 'MODIFY':
                # Obter os dados do novo/modificado item
                new_image = record['dynamodb'].get('NewImage')
                
                # Converter o formato DynamoDB para Python
                laudo = {k: v[list(v.keys())[0]] for k, v in new_image.items()}
                
                evaluation_id = laudo.get('evaluation_id')
                user_id = laudo.get('user_id')
                valor_troca = laudo.get('valor_troca')
                
                if not valor_troca:
                    print(f"Laudo ID {evaluation_id} sem valor de troca. Ignorando.")
                    continue

                # 2. Lógica de Sugestão de Troca
                # Define uma faixa de preço aceitável (ex: até 1500 a mais que o valor de troca)
                valor_maximo_sugerido = valor_troca + 1500.00
                
                sugestoes = [
                    modelo for modelo in ESTOQUE_MODELOS 
                    if modelo['valor_mercado'] <= valor_maximo_sugerido
                ]
                
                if not sugestoes:
                    sugestao_final = "Nenhuma sugestão de troca encontrada dentro da faixa de preço."
                else:
                    # Escolhe uma sugestão aleatória para simplificar
                    sugestao = random.choice(sugestoes)
                    diferenca = sugestao['valor_mercado'] - valor_troca
                    
                    sugestao_final = (
                        f"Seu laudo foi concluído! Valor de troca: R$ {valor_troca:.2f}. "
                        f"Sugestão: {sugestao['modelo']} por mais R$ {diferenca:.2f}. "
                        f"Ganhos: {sugestao['ganhos']}."
                    )

                # 3. Enviar Notificação (SNS)
                # Em um ambiente real, o user_id seria usado para buscar o endpoint de notificação (ex: token push)
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=sugestao_final,
                    Subject=f"Resultado da Avaliação {evaluation_id} e Sugestão de Troca"
                    # Para enviar para um usuário específico, usaríamos TargetArn ou EndpointArn
                )
                
                print(f"Notificação enviada para o usuário {user_id}. Sugestão: {sugestao_final}")

        return {'statusCode': 200, 'body': 'Sugestões de troca processadas com sucesso'}

    except Exception as e:
        print(f"Erro ao sugerir troca: {e}")
        raise e
dados_membro = {
    'user_id': 1,
    'name': 'Fulano de Tal',
    'function': 'Desenvolvedor',
    'address': 'Rua Exemplo, 123',
    'birth_date': '01/01/1990',
    'status': 'Ativo'
}

gerador = CardGenerator()
caminho_carteirinha = gerador.generate_card(dados_membro)

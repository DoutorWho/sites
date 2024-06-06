import sqlite3
class Pessoas:    
    @staticmethod
    def perfil(perfil_do_usuario, perfil_status, meucpf=None):
        # aqui ele inicializa o cursor e a conexão
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # aqui ele verifica se o usuário existe! A foto do perfil é mera ilustração!
        cursor.execute("""
            SELECT * FROM Pessoas
                where nome_perfil = ?""",(perfil_do_usuario,))    
        perfil = cursor.fetchone()
        if perfil == None:
            return ['erro']

        # aqui ele vai pegar os dados do usuário e o número de comentários
        cpf = perfil[3]
        cursor.execute("""SELECT nome, idProduto FROM AvaliacaoProdutos
            WHERE cpf = ?""",(cpf,))
        avaliacao = cursor.fetchall() #fetchall, fetchone e fetchmany
        if avaliacao == []:
            avaliacao = [] # no caso 0 produtos!
        else:
            avaliacao = list(map(lambda x: list([x[0], x[0] + '/' + str(x[1])]), avaliacao)) # [('Hambúrgueres Doces', 2), ('Trufa de Chocolate', 6), ('Brigadeiro Gourmet', 7)]  
            quantidade = len(avaliacao)
            for numero in range(quantidade):
                if numero < quantidade-2:
                    avaliacao[numero][0] = avaliacao[numero][0]  + ', '
                elif numero < quantidade-1:
                    avaliacao[numero][0] = avaliacao[numero][0]  + ' e '
                else:
                    avaliacao[numero][0] = avaliacao[numero][0]  + '.'
        foto_perfil =  'imagens_usuarios/' + perfil[7]
        # se o usuário for outro, as informações serão limitadas!
        if perfil_status == 'outro':
            cursor.execute(""" 
                SELECT foto_de_perfil FROM Pessoas
                where cpf = ?""",(meucpf,))    
            foto_usuario_perfil = 'imagens_usuarios/' + cursor.fetchone()[0] # aqui é pra garantir que em imagem a foto de perfil será dele!
            pasta = {'nome_usuario':  perfil[1].capitalize(), 'nome_perfil': '@'  + str(perfil[2]), 'sexo': perfil[5], 'foto_de_perfil': foto_perfil, 'total_de_comentario': perfil[8], 'avaliacao': avaliacao}
            return [pasta, foto_usuario_perfil]


        # se o usuário não for outro, obviamente é ele próprio, então, tem mais informações!
        cursor.execute("""SELECT idNotificacao, remetente, produto, mensagem, status FROM Notificacao
            WHERE destinatario = ?""",(perfil[2],))
        resposta = cursor.fetchall() 
        # preparando dados das notificações
        quantidade = len(resposta)
        notificacoes = {'idNotificacao': [], 'remetente': [], 'mensagem': [], 'url_produto': [], 'url_comentario': [],  'visualizacao': [], 'quantidade': quantidade}
        if resposta == []:
            notificacoes = None
            quantidade_notificao = 0
        else:
            for mensagem in resposta:
                notificacoes['idNotificacao'].append(mensagem[0])
                notificacoes['remetente'].append(mensagem[1])
                urls = mensagem[2].split("#")
                notificacoes['url_produto'].append(urls[0])
                notificacoes['url_comentario'].append(urls[1])
                notificacoes['mensagem'].append(mensagem[3])
                notificacoes['visualizacao'].append(bool(mensagem[4]))
            quantidade_notificao = notificacoes['visualizacao'].count(False)
            notificacoes['quantidade_notificao'] = quantidade_notificao # aqui ele já gera isso!
        #[('Trufa de Chocolate/6#comentario1', 'É mesmo rapá! Virei ...', 0), ('Trufa de Chocolate/6#comentario1', 'É mesmo rapá! Virei ...', 0)] 
        pasta = {'nome_usuario': perfil[1].capitalize(), 'nome_perfil': '@'  + str(perfil[2]), 'cpf': perfil[3], 'email': perfil[4], 'sexo': perfil[5], 'foto_de_perfil': foto_perfil, 'cidade': perfil[6], 'total_de_comentario': perfil[8], 'avaliacao': avaliacao,'notificacoes': notificacoes, 'quantidade_notificacao': quantidade_notificao} # arquivo que vai ser retornado!
        return [pasta, foto_perfil]

    @staticmethod
    def logar(email: str, senha_enviada: str):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT nome_usuario, nome_perfil, CPF, senha FROM Pessoas 
        where email = ?;""",(email,))
        dados = cursor.fetchall() 
        if dados == []:
            return [False, 'usuário não existe'] # 1 de usuário não existe

        nome_usuario = dados[0][0]
        nome_perfil = dados[0][1]
        cpf = dados[0][2]
        senha = dados[0][3]
        conexao.close()
        senha_cadastrada = senha
        if senha_cadastrada != senha_enviada: # Ou seja, se e ele errou a senha!
            return [False, 'senha inválida'] # 2 de senha inválida!

        return [True, nome_usuario, nome_perfil, cpf]

    @staticmethod
    def tirar_notifacoes(nome, visto, idNotificacao):
        try:
            visto = bool(visto)
        except ValueError:
            return
        if visto:
            conexao = sqlite3.connect("bancodedados.db")
            cursor = conexao.cursor()  
            cursor.execute(""" 
                SELECT status FROM Notificacao
                where idNotificacao = ? and destinatario = ?""",(idNotificacao, nome))
            status = cursor.fetchone() # aqui é pra garantir que ngm vai fazer graça, que nem os usuários!
            print("O status é", status)
            if status == None:
                return
            if status[0] == 1:
                return
            cursor.execute(""" 
                Update Notificacao
                set
                    status = ?
                where idNotificacao = ? and destinatario = ?""",(True, idNotificacao, nome))
            conexao.commit()
            conexao.close()
            return

    @staticmethod
    def verificar_id_foto(cpf=None):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        if cpf == None:
            cursor.execute("SELECT count(idPessoas) from Pessoas")
            id_da_pessoa = str(int(cursor.fetchone()[0]) + 1)
        else:
            cursor.execute(""" 
                SELECT idPessoas from Pessoas
                where cpf = ?""",(cpf,))
            id_da_pessoa = str(cursor.fetchone()[0])
        conexao.close()
        return id_da_pessoa
    @staticmethod
    def adicionar_usuario(nome_usuario: str, nome_perfil: str, cpf: str, email: str, sexo: str, cidade: str, foto_de_perfil: str, senha: str):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                           INSERT INTO Pessoas(nome_usuario, nome_perfil, CPF, email, sexo, cidade, foto_de_perfil, total_de_comentario, senha) Values
                           (?, ?, ?, ?, ?, ?, ?, 0, ?)""",(nome_usuario, nome_perfil, cpf, email, sexo, cidade, foto_de_perfil, senha))
            conexao.commit()
        except sqlite3.IntegrityError as erro: # Ou seja, deu no unique
            erro = str(erro)
            if erro == 'UNIQUE constraint failed: Pessoas.nome_perfil':
                nome_erro = 'Esse nome já existe'
            elif erro == 'UNIQUE constraint failed: Pessoas.CPF':
                nome_erro = 'Esse CPF já existe'
            else:
                nome_erro = 'Esse email já existe!'
            conexao.close()
            return [False, nome_erro]
        return [True]
    @staticmethod
    def alterar_ususario(cpf: str, nome_usuario: str, cidade: str, foto: str, senha: str):
        from os import remove, path, getcwd
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # coloca pra excluir a foto aqui! No caso pegando o email e exlcuindo a foto antiga!
        cursor.execute(""" 
            SELECT foto_de_perfil FROM Pessoas
            where email = ?""",(cpf,))
        foto_excluir = cursor.fetchone()[0]
        try:
            remove(path.join(getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usarios' + f'\\{foto_excluir}')) # Para remover o arquivo!
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        # Colocando a foto no caminho certo, verificação de id
        id_da_pessoa_com_foto = Pessoas.verificar_id_foto(cpf) + '_' + foto
        # Alterando os dados, a partir do email, já que é único!
        cursor.execute(""" 
            Update Pessoas
                set 
                    nome_usuario = ?,
                    foto_de_perfil = ?,
                    cidade = ?
                    senha = ?,
            where cpf = ?""",(nome_usuario, id_da_pessoa_com_foto, cidade, senha, cpf))
        conexao.commit()
        conexao.close()
        return id_da_pessoa_com_foto
    @staticmethod
    def enviar_cookie(informacao_entrada, cookies):
        # fazer a parte dos cookies!
        # os de de entrada vai da como parâmetro as novas informacoes
        entrada = informacao_entrada # aqui seria [Nome do produto, id do produto]
        produto = cookies['Acessos'].get(entrada[0], None)
        if produto == None:
            cookies['Acessos'][entrada[0]] = 1
        else:
            cookies['Acessos'][entrada[0]] += 1
        # agora descobrir o tipo do produto
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT tipo FROM Produtos
            where idProdutos = ?""",(entrada[1],))
        tipo_produto = cursor.fetchone()[0]
        # agora adicionado esse tipo!
        tipo = cookies['Tipos_produtos'].get(tipo_produto, None)
        if tipo == None:
            cookies['Tipos_produtos'][tipo_produto] = 1
        else:
            cookies['Tipos_produtos'][tipo_produto] += 1
        conexao.close()
        return cookies

    @staticmethod
    def pegar_cookie(cookies):
        from random import sample
        # #{"Acessos": {"Hambúrgueres Doces": 3, "Torta de Limão": 4}, "Tipos_produtos": {"doces_frescos": 3, "doces_relaxantes": 4}}
        acessos = cookies['Acessos']
        if acessos == {}:
            return None
        tipos_produto = cookies['Tipos_produtos']
        maior_acesso = max(acessos, key=acessos.get) # aqui ele retorna o que tem mais acessos
        maior_tipo_produto = max(tipos_produto, key=tipos_produto.get)
        # agora eu vou listar 3 produtos do tipo preferido dele, os produtos serão escolhidos aleatoriamente 
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT nome FROM Produtos
            WHERE tipo = ?""",(maior_tipo_produto,))
        lista_produtos_tipo = cursor.fetchall()
        quantidade = min(5, len(lista_produtos_tipo))  # Isos é pra garantir algumas condições! Pq, k=5 não pega, pois tem produtos não batem 5! Aí ele faz, entre 5 e quantidade, qual é o menor? No caso se quantidade for 8, ele vai pegar 5, se quantidade for 3, ele pega 3.
        tipos_lista = [nome[0] for nome in sample(lista_produtos_tipo, k=quantidade)]
        tipos_lista.append(maior_acesso)
        tipos_lista = set(tipos_lista)
        conexao.close()
        return tipos_lista
    @staticmethod
    def excluir_ususario(cpf):
        from os import remove, path, getcwd
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # exclui a foto de perfil
        cursor.execute(""" 
            SELECT foto_de_perfil FROM Pessoas
            where cpf = ?""",(cpf,))
        foto_excluir = cursor.fetchone()[0]
        try:
            remove(path.join(getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usarios' + f'\\{foto_excluir}')) # Para remover o arquivo!
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        # pegando o id pra excluir a conta!
        cursor.execute("""SELECT idPessoas FROM Pessoas
            where cpf = ?""",(cpf,))
        idPessoa = cursor.fetchone()[0]

        # excluir a conta
        cursor.execute(""" 
            DELETE FROM Pessoas
            where cpf = ?""",(cpf,))
        conexao.commit()

        cursor.execute(""" 
            DELETE FROM Carrinho
            where idPessoas = ?""",(idPessoa,))
        conexao.commit()

        cursor.execute(""" 
            DELETE FROM Compra
            where idPessoas == ?""",(idPessoa,))
        conexao.commit()

        cursor.execute(""" 
            DELETE FROM Comentarios
            where idPessoa = ?""",(idPessoa,))
        conexao.commit()

        cursor.execute(""" 
            DELETE FROM Notificacao
            where idPessoas = ?""",(idPessoa,))
        conexao.commit()
        conexao.close()

class Produtos:
    @staticmethod
    def adicionar_produto(tipo: str, nome: str, descricao: str, ingredientes: str, imagem: str, preco):
        """ 
        # Função que adiciona produtos ao site!

        `Utilização`:

        - tipo: Existem somente três tipos!
        - nome: Escolha o nome do produto.
        - descricao: Escolha a descrição do produto!
        - imagem: Escolha uma imagem que esteja em img/compras! No caso nessa url, caso o contrário, não vai funcionar! Mande somente o nome dela!
        - preco: Digite o preco! 
    
        Exemplo
        .. code-block:: python
        Produtos.adicionar_produto("para comer",'Macarrão', "é gostoso", 'maracao.jpeg', "25,90")
        """
        # verificando exceções 2.78
        if tipo not in ['doces_frescos', 'doces_intensos', 'doces_relaxantes']:
            raise SyntaxWarning("Tipo inválido! Digite um tipo de doce válido!")
        if isinstance(preco, float):
            add = str(preco).split('.')
            preco = str(preco) + '0' if len(add[1]) == 1 else str(preco)
        try:
            valor = float(str(preco).replace(',', '.'))
            del valor
        except:
            raise ValueError('Por favor, digite um preco válido para o produto!')
        preco = str(preco).replace('.',',') # aqui é pra garantir o código certo! Ou seja, com ',' ao invés de '.'!

        teste = str(imagem)
        if teste.count('.') == 1:
            teste1 = teste.split(".")
            if teste1[1] in ['jpeg', 'png', 'jpg']:
                pass
            else:
                raise SyntaxError("Tipo inválido, só aceitamos jpg ou png!")
        else:
            raise SyntaxError("Por favor, digite o tipo do produto! Ou seja, se é jpeg ou png!")

        # código
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO Produtos(tipo, nome, descricao, ingredientes, imagem, preco) Values
            (?, ?, ?, ?, ?, ?);
            """,(tipo, nome, descricao, ingredientes, imagem, preco))
        conexao.commit()
        conexao.close()
        print(f"O produto {nome} foi adicionado com sucesso!")
    @staticmethod
    def lista_produtos():
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM Produtos""")
        produtos = cursor.fetchall()
        conexao.close()
        return produtos
    @staticmethod
    def add_carrinho(cpf, idProduto, quantidade):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT idPessoas FROM Pessoas
            where cpf = ?""",(cpf,))
        idUsuario = cursor.fetchall()[0][0]
        cursor.execute(""" 
            INSERT INTO Carrinho(idPessoas, produto, quantidade) Values
            (?, ?, ?)""",(idUsuario, idProduto, quantidade))
        conexao.commit() # o PREÇO DO PRODUTO EU SEI A PARTIR DO PRODUTO!
        conexao.close()
    @staticmethod
    def ver_carrinho(cpf):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT idPessoas FROM Pessoas
            WHERE cpf = ?""",(cpf,))
        idPessoas = cursor.fetchall()[0][0]
        cursor.execute("""
            SELECT * FROM Carrinho
            WHERE idPessoas = ?""",(idPessoas,))
        produtos_no_carrinho = cursor.fetchall() # são os itens que estão no carrinho! O item 3 é o id
        cursor.execute("SELECT * FROM Produtos")
        produtos_disponiveis = cursor.fetchall() # são todos os produtos disponíveis
        carrinho_usuario = []
        for carrinho in produtos_no_carrinho:
            for produtos in produtos_disponiveis:
                if carrinho[2] == produtos[0]: # Aqui é o seguinte, o id do produto no carrinho é igual ao id do produto normal! Se for ele
                    # se for ele executa isso, para pegar o produto!
                    preco = produtos[6]
                    quantidade = int(carrinho[3])
                    itens = [carrinho[0], produtos[1], produtos[2], produtos[3], produtos[5], preco, quantidade] 
                    carrinho_usuario.append(itens.copy())
                    itens.clear()
                    break
        return carrinho_usuario
    @staticmethod
    def comprar_excluir(status, idCarrinho=None, dados={}): 
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        if status == 'comprar':
            dados_para_enviar = dados.copy()
            lista = list()
            quantidade = len(dados['produtos'])
            pagamento = 0
            for posicao in range(quantidade): # aqui vai zerar os dois app!
                # para simplesmente adicionar a imagem
                cursor.execute("""
                    SELECT imagem FROM Produtos
                    where nome = ?""",(dados['produtos'][posicao],))
                imagem = cursor.fetchone()[0]
                lista.append(imagem)
                # ----------------
                cursor.execute("""
                    DELETE FROM Carrinho
                    where idCompra = ?""",(dados['idCarrinhos'][posicao],))
                conexao.commit()
                pagamento += float(dados['precos_totais'][posicao]) * float(dados['quantidades_totais'][posicao])
            dados_para_enviar['imagem'] = lista
            dados_para_enviar['totalpago'] = format(pagamento, ".2f").replace('.',',')
            conexao.close()
            return dados_para_enviar
        if status == 'excluir':
            cursor.execute("""
                DELETE FROM Carrinho
                where idCompra = ?""",(idCarrinho,))
            conexao.commit()
        conexao.close()
    @staticmethod
    def produtos_descricao(nome_produto: str, id_produto):
        try:
            id_produto = int(id_produto)
        except ValueError:
            return 'houve erro'
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT * FROM Produtos
            where nome = ? and idProdutos = ?""",(nome_produto, int(id_produto)))
        try:
            lista_produto = cursor.fetchall()[0]
        except IndexError:
            return ['Erro']
        finally:
            conexao.close()
        return lista_produto

    @staticmethod
    def avaliar_produto(cpf, idProduto, nome, avaliacao):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT cpf FROM AvaliacaoProdutos  
            where cpf = ? and idProduto = ?""",(cpf, idProduto)) # isso daqui é só pra vê se ele já votou ou não!
        resultado = cursor.fetchone()
        if resultado == None: # isso significa que ele não votou naquele produto | Eu posso descobrir a avaliação de um produto somando todos os produtos pelo total de pessoa que avaliou ele!
            cursor.execute(""" 
                INSERT INTO AvaliacaoProdutos(cpf, idProduto, nome, avaliacao_pontuacao) Values
                    (?, ?, ?, ?);""",(cpf, idProduto, nome, avaliacao))
        else:
            cursor.execute(""" 
                Update AvaliacaoProdutos
                    SET
                        avaliacao_pontuacao = ?
                    WHERE cpf = ? and idProduto = ?""",(avaliacao, cpf, idProduto))
        conexao.commit()
        conexao.close()
    @staticmethod
    def ver_avaliacao(idProduto=0): 
        from math import ceil
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor() # ★
        if idProduto != 0:
            cursor.execute(""" 
                SELECT * FROM AvaliacaoProdutos
                where idProduto = ?""",(idProduto,))
            resultado = cursor.fetchall()
            quantidade_votos = len(resultado)
            conexao.close()
            if resultado == []: # {'avaliacao_principal': avaliacao_principal, 'quantidades_avaliacacoes': quantidades_avaliacacoes}
                return {'avaliacao_principal': '✰ ﹀ 0', 'quantidades_avaliacacoes': {'1 estrela' if numero == 1 else f'{numero} estrelas': '0%'  for numero in range(5)}}
            numero_avaliacao = []
            for idAvalicao in resultado:
                if idAvalicao[2] == idProduto:
                    numero_avaliacao.append(idAvalicao[4])
            total_avaliacoes = len(numero_avaliacao)
            resposta = sum(numero_avaliacao) / total_avaliacoes
            avaliacao_principal = f"{str(resposta).replace('.',',')} | {'★' * ceil(resposta)} ﹀ {quantidade_votos}"
            # aqui eu tento descobrir as quantidades de 1, 2, 3, 4 e 5
            quantidades_avaliacacoes = {}
            for quantidade in range(1, 6):
                quantidades_avaliou = numero_avaliacao.count(quantidade)
                porcentagem = f"{(quantidades_avaliou/total_avaliacoes)*100:.2f}%" 
                quantidades_avaliacacoes[f'{quantidade} {'estrela' if quantidade == 1 else 'estrelas'}'] = porcentagem
            return {'avaliacao_principal': avaliacao_principal, 'quantidades_avaliacacoes': quantidades_avaliacacoes} # Aqui eu somo o resultado e divido!


        # tipo normal, então faz
        cursor.execute("SELECT nome FROM Produtos")
        produtos = cursor.fetchall()
        cursor.execute("SELECT nome, avaliacao_pontuacao FROM AvaliacaoProdutos")
        resultado = cursor.fetchall()
        lista_avaliacao = {}
        for produto in produtos:
            produto_avaliado = False
            for avaliar in resultado:
                if produto[0] == avaliar[0]: 
                    cursor.execute("""SELECT count(idProduto) FROM AvaliacaoProdutos
                        where nome = ?""",(avaliar[0],)) # Aqui é pra saber quantos vezes esse produto foi avaliado!
                    total_avaliacao = cursor.fetchone()[0]

                    cursor.execute("""SELECT sum(avaliacao_pontuacao ) FROM AvaliacaoProdutos
                        where nome = ?""",(avaliar[0],)) # Aqui é pra saber o total de notas avaliados naquele nome!
                    total_nota_avaliacao = cursor.fetchone()[0]
                    resposta = total_nota_avaliacao / total_avaliacao
                    lista_avaliacao[avaliar[0]] = f"{str(resposta).replace('.', ',')} | {'★' * ceil(resposta)} ﹀ {total_avaliacao}"
                    produto_avaliado = True
                    break
            if produto_avaliado == False:
                lista_avaliacao[produto[0]] = f"✰ ﹀ 0"
        conexao.close()
        return lista_avaliacao
# [(1, 'leandro', 6, 'Trufa de Chocolate', 5.0)]    
class Compra:
    from datetime import datetime, timedelta
    from random import randint
    @classmethod
    def pagamento(cls, chave_pix='', dados=[], status='pagar'):
        import json
        if status == 'gerar_pagamento':
            with open("arquivos/pagamento.json", 'r', encoding='utf-8') as arquivo_json:
                dados_json = json.load(arquivo_json)
                dados_json['valores'].append(f"{chave_pix}")

            with open("arquivos/pagamento.json", 'w', encoding='utf-8') as arquivo_json:
                json.dump(dados_json, arquivo_json, indent=2, separators=(',', ': '), ensure_ascii=False)
            return
        # aqui é o status='pagar'
        # aqui a informação será o número pix!
        with open("arquivos/pagamento.json", 'r', encoding='utf-8') as arquivo_json:
            dados_json = json.load(arquivo_json)
        with open("arquivos/pagamento.json", 'w', encoding='utf-8') as arquivo_json:
            if chave_pix in dados_json['valores']: # aqui é pra vê se a chave está contida em dados!
                dados_json['valores'].remove(chave_pix)
                json.dump(dados_json, arquivo_json, indent=2, separators=(',', ': '), ensure_ascii=False)
            else:
                json.dump(dados_json, arquivo_json, indent=2, separators=(',', ': '), ensure_ascii=False)
        # aqui é para adicionar isso em compras, ou seja, nas compras do usuário
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # pegar o id do usuário
        cursor.execute("""
            SELECT idPessoas FROM Pessoas
            where cpf = ?""",(dados[0],))
        idPessoas = cursor.fetchone()[0]

        # aqui já é a parte de adicionar no banco de dados
        quantidade = len(dados[1]['produtos'])
        #data_compra = f"{cls.datetime.today().day:02d}/{cls.datetime.today().month:02d}/{cls.datetime.today().year}"
        #data_compra = cls.datetime.strptime(data_compra, "%d/%m/%Y")
        data_compra_objeto = cls.datetime.now()
        data_compra = cls.datetime.strftime(data_compra_objeto, "%d/%m/%Y") 
        for contagem in range(quantidade):
            tempo_entrega = data_compra_objeto +  cls.timedelta(days=cls.randint(5, 20)) 
            data_entrega = cls.datetime.strftime(tempo_entrega, "%d/%m/%Y")
            cursor.execute(""" 
                INSERT INTO Compra(idPessoas, produto, frete, preco, quantidade, data_compra, data_entrega, status) Values
                (?, ?, ?, ?, ?, ?, ?, ?)""",(idPessoas, dados[1]['produtos'][contagem], dados[1]['frete'][contagem], dados[1]['precos_totais'][contagem], dados[1]['quantidades_totais'][contagem], data_compra, data_entrega, 'Enviando produto'))
            conexao.commit()
        conexao.close()
    @classmethod
    def compras_status(cls, cpf, produtos):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()

        # pegar os produtos para acessar preços
        cursor.execute("SELECT * FROM PRODUTOS")
        produtos_todos = cursor.fetchall()

        # pegar o id do usuário
        cursor.execute("""
            SELECT idPessoas FROM Pessoas
            where cpf = ?""",(cpf,))
        idPessoas = cursor.fetchone()[0]
        cursor.execute(""" 
            SELECT idCompra, produto, preco, quantidade, data_compra, data_entrega, status FROM Compra
            where idPessoas = ?""",(idPessoas,))
        registros = cursor.fetchall()
        lista_compras = []
        data_atual = cls.datetime.today()
        for registro in registros:
            data_compra = cls.datetime.strptime(registro[4], "%d/%m/%Y") 
            data_entrega = cls.datetime.strptime(registro[5], "%d/%m/%Y")
            if (data_atual >= data_entrega):
                status = 'Entregue ao destinatário'
            elif (data_atual >= (data_compra + cls.timedelta(days=1))):
                status = 'Preparando o envio'
            elif ((data_atual >= data_compra + cls.timedelta(days=3))):
                status = 'Enviando para a transportadora'
            else:
                status = 'Enviando'
            lista_compras.append({'idCompra': registro[0], "Nome": registro[1], 'Preco': registro[2], 'quantidade': registro[3], 'data_compra': registro[4], 'data_chegada': registro[5], 'status': status})
        # atualizando no banco de dados!
        for atualizar in lista_compras:
            cursor.execute(""" 
                Update Compra
                set status = ?
                where idCompra = ? and idPessoas = ? """,(atualizar['status'], atualizar['idCompra'], idPessoas))
            conexao.commit()
        cursor.execute("""
            SELECT * FROM Compra
            where idPessoas = ?""",(idPessoas,))
        conexao.close()
        # em produtos eu tenho a lista dos produtos
        for posicao, compras in enumerate(lista_compras):
            nome = compras['Nome']
            for adicionar_imagem in produtos: # aqui é para adicionar imagem em produtos!
                if nome == adicionar_imagem[2]:
                    lista_compras[posicao]['imagem'] = adicionar_imagem[4]
                    lista_compras[posicao]['imagem'] = adicionar_imagem[5]
                    break
        return lista_compras

class Comentario():
    @staticmethod
    def adicionar_comentario(comentario, idProduto, remetente, cpf='nenhum', nome_id_produto=''):
        from datetime import datetime
        hora_e_data = datetime.today()
        data = datetime.strftime(hora_e_data, '%d/%m/%Y')
        hora = datetime.strftime(hora_e_data, '%H:%M')
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT nome_perfil, idPessoas FROM Pessoas
            where cpf = ?""",(cpf,))
        dados = cursor.fetchall()[0]
        nome_perfil = dados[0]
        idPessoa = dados[1]
        cursor.execute(""" 
            INSERT INTO Comentarios(idPessoa, idProduto, data_do_comentario, hora_do_comentario, comentario, remetente) Values
            (?, ?, ?, ?, ?, ?)""",(idPessoa, idProduto, data, hora, comentario, remetente))
        conexao.commit()
        cursor.execute(""" 
            Update Pessoas
                SET
                    total_de_comentario = total_de_comentario  + 1
                WHERE idPessoas = ?""",(idPessoa,))
        conexao.commit()

        # verificando se no comentário do usuário há alguma menção
        comentario = str(comentario) + ' ' # esse espaço é só pra resolver falha do "aaa @leandro", pois ele da erro, não tem final!
        ultima_ocorrencia = 8 # so pro erro sumir
        quantidade_arroba = comentario.count("@")
        if quantidade_arroba >= 1:
            indice_novo = 0 # para garantir que todos os indices serão enviados!
            for contagem in range(quantidade_arroba):
                primeira_ocorrencia = comentario.index("@", indice_novo) # agora eu tenho que separar por , . ! ? ' '
                comentario_arroba = comentario[primeira_ocorrencia:]
                indice_novo = primeira_ocorrencia + 1 # pra gerar um novo índice!
                for posicao, fim in enumerate(comentario_arroba):
                    if fim in [' ', ',', '.', '!', '?']:
                        ultima_ocorrencia = (primeira_ocorrencia + posicao)
                        break
                pessoa = comentario[primeira_ocorrencia:ultima_ocorrencia].replace('@', '') # so pra saber no banco de dados se existe!
                cursor.execute(""" 
                    SELECT nome_perfil FROM Pessoas
                    where nome_perfil = ?""",(pessoa,))
                resposta = cursor.fetchone()
                if resposta != None:
                    if pessoa != nome_perfil: # quer dizer que não é a mesma pessoa!
                        comentario_da_pessoa = comentario[:20] + '...'
                        if contagem == 0: # aqui é pra garantir que não vai ficar dando erro no nome do produto, pra ser endereçado! Por conta do join, que vai separar os itens mesmo eles já estando separados!
                            cursor.execute("SELECT count(idComentarios) FROM Comentarios") # se ele tá adicionando o comentário agora, então o id atual é o id de agora.
                            id_comentario_atual = cursor.fetchone()[0] # serve para eu usar na menção! Pra saber o produto só passar como parâmetro o site produto!
                            nome_id_produto = f"{'/'.join(nome_id_produto)}#comentario{id_comentario_atual}"
                            cursor.execute(""" 
                            INSERT INTO Notificacao(remetente, destinatario, produto, mensagem, status) Values
                            (?, ?, ?, ?, False);""",(nome_perfil, pessoa, nome_id_produto, comentario_da_pessoa))
                            conexao.commit()
        conexao.close()

    @staticmethod
    def remover_comentario(idComentario, cpf):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()   
        cursor.execute(""" 
            DELETE FROM Comentarios
            where idComentarios = ? or remetente = ?""",(idComentario, idComentario))
        conexao.commit()
        cursor.execute(""" 
            Update Pessoas
                SET
                    total_de_comentario = total_de_comentario - 1
                WHERE cpf  = ?""",(cpf,))
        conexao.commit()
        conexao.close()
        
    @staticmethod
    def ver_comentarios(produto=6): # aqui é qual produto da mensagem. Da pra saber o produto pela URL que fiz lá no main.
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # aqui é pra mostrar os comentários
        cursor.execute("""
            SELECT * FROM Comentarios
            where idProduto = ?""",(produto,))
        todos_comentario = cursor.fetchall()
        cursor.execute("SELECT * FROM Pessoas")
        todas_pessoas = cursor.fetchall()
        # o vetor eu quero [todos_comentario] + nome, sexo e foto_de_perfil
        comentarios_principais = [] # são vários comentários
        resposta_comentarios = []
        for pessoa in todas_pessoas:
            idPessoa = pessoa[0]
            for comentario in todos_comentario:
                if comentario[1] == idPessoa:
                    remetente = None if comentario[6] == 'None' else comentario[6]
                    cursor.execute(""" 
                        SELECT produto FROM Compra
                        where idPessoas = ?""",(pessoa[0],))
                    compra_verificada = True if cursor.fetchone() != None else False
                    cursor.execute(""" 
                        SELECT * FROM AvaliacaoProdutos
                        where cpf == ? and idProduto = ?""",(pessoa[3],produto)) # aqui eu descubro se é nesse cpf e nesse produto!
                    avaliacao_resposta = cursor.fetchone()
                    avaliacao = 'Não avaliou' if avaliacao_resposta == None else f"Avaliação: {str(avaliacao_resposta[4]).replace('.',',')}"

                    # aqui é para colocar o negócio azul em comentário no @. Lembrando que isso é um loop!

                    comentario_da_pessoa = comentario[5] # aqui é o comentário que será substituído
                    comentario_teste = str(comentario[5]) + ' '  # só por causa do ' ', eu preciso disso, mas ele não altera o comentário original!
                    quantidade_arroba = comentario_teste.count('@') # aqui é a quantidade de arroba, que tem em um comentário
                    # isso aqui é pra eu saber os nomes que estão no @.
                    if quantidade_arroba >= 1:
                        indice_novo =  0 
                        lista_nomes = [] 
                        for contagem in range(quantidade_arroba): # aqui é pra garantir que todos tenham o @ com strong em azul.
                            primeira_ocorrencia = comentario_teste.index("@", indice_novo) 
                            indice_novo = primeira_ocorrencia + 1 # aqui é pra garantir que ele vai em ocorrência por ocorrência
                            comentario_arroba = comentario_teste[primeira_ocorrencia:]
                            for posicao, fim in enumerate(comentario_arroba):
                                if fim in [' ', ',', '.', '!', '?']:
                                    ultima_ocorrencia = (primeira_ocorrencia + posicao) # a última posição é sempre ignorada!
                                    substituir = comentario_teste[primeira_ocorrencia:ultima_ocorrencia]
                                    lista_nomes.append(substituir) # aqui eu tenho o nome!
                                    break
                        lista_nomes = list(set(lista_nomes)) # aqui é para garantir que se os nomes forem repetidos, não terás erros! Pois o set garante isso! Aí aqui aparece a lista de nomes daquele comentário!
                        for nome in lista_nomes: # aqui a partir da lista de nomes eu adiciono o que se deve.
                            texto = f"""<a href="/perfil/{nome.replace('@','')}" target="_blank"><strong id='chamado'>{nome}</strong></a>"""
                            comentario_da_pessoa = comentario_da_pessoa.replace(nome, texto)

                    # e aqui o código continua normal
                    if remetente == None:
                        comentarios_principais.append({'idComentario': comentario[0], 'nome_usuario': pessoa[1], 'nome_perfil': '@' + pessoa[2], 'data_de_envio_e_hora': f"{comentario[3]} às {comentario[4]}", 'comentario': comentario_da_pessoa, 'imagem': pessoa[7], 'compra_verificada': compra_verificada, 'avaliacao': avaliacao})
                    else:
                        resposta_comentarios.append({'idComentario': comentario[0], 'nome_usuario': pessoa[1], 'nome_perfil': '@' + pessoa[2], 'data_de_envio_e_hora': f"{comentario[3]} às {comentario[4]}", 'comentario': comentario_da_pessoa, 'imagem': pessoa[7], 'remetente': int(comentario[6]), 'compra_verificada': compra_verificada, 'avaliacao': avaliacao })
        conexao.close()
        comentarios_principais = sorted(comentarios_principais, key=lambda x: x['idComentario'], reverse=True)
        resposta_comentarios = sorted(resposta_comentarios, key=lambda x: x['idComentario'])
        return [comentarios_principais, resposta_comentarios]

'''conexao = sqlite3.connect("bancodedados.db")
cursor = conexao.cursor()
cursor.execute("SELECT * FROM Notificacao")
print(cursor.fetchall())
conexao.close()'''
import sqlite3
if __name__ == '__main__':
    conexao = sqlite3.connect("bancodedados.db")
    cursor = conexao.cursor()


class Pessoas:    
    @staticmethod
    def perfil(email):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM Pessoas
            where email = ?""",(email,))    
        perfil = cursor.fetchone()
        arquivo =  'imagens_usarios/' + perfil[4]
        sexo = 'Masculino' if perfil[3] == 'M' else 'Feminino'
        pasta = [perfil[1], perfil[2], sexo, arquivo, str(perfil[5]).title(), perfil[6], str(perfil[8]).replace('.', ',')] # arquivo que vai ser retornado!
        return pasta
    @staticmethod
    def logar(email, senha):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT nome, senha FROM Pessoas 
        where email = ?;""",(email,))
        nome = cursor.fetchall() 
        conexao.close()
        if nome == []:
            return [False, 'usuário não existe'] # 1 de usuário não existe

        senha_cadastrada = nome[0][1]
        if senha_cadastrada == senha:
            return [True, nome[0][0]]

        return [False, 'senha inválida'] # 2 de senha inválida!
    @staticmethod
    def verificar_id_foto(email=None):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        if email == None:
            cursor.execute("SELECT count(idPessoas) from Pessoas")
            id_da_pessoa = str(int(cursor.fetchone()[0]) + 1)
        else:
            cursor.execute(""" 
                SELECT idPessoas from Pessoas
                where email = ?""",(email,))
            id_da_pessoa = str(cursor.fetchone()[0])
        conexao.close()
        return id_da_pessoa
    @staticmethod
    def adicionar_usuario(nome, email, sexo, foto_de_perfil, forma_de_pagamento, preferencia, senha):
        nome = str(nome).title() # para deixar bonito!
        if sexo == 'Masculino':
            sexo = 'M'
        else:
            sexo = 'F'
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM Pessoas
            where email = ?""", (email,))
        email_cadastrado = cursor.fetchall()
        if email_cadastrado == []: # Se isso for igual, é pq não existe esse email cadastado!
            cursor.execute("""
                           INSERT INTO Pessoas(nome, email, sexo, foto_de_perfil, forma_de_pagamento, preferencia, senha, dinheiro) Values
                           (?, ?, ?, ?, ?, ?, ?, 2000)""",(nome, email, sexo, foto_de_perfil, forma_de_pagamento, preferencia, senha))
            conexao.commit()
            conexao.close()
            return True
        return False
    @staticmethod
    def alterar_ususario(email, nome, sexo, forma_de_pagamento, preferencia, foto, senha):
        from os import remove, path, getcwd
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        if sexo == 'Masculino':
            sexo = 'M'
        else:
            sexo = 'F'
        # coloca pra excluir a foto aqui! No caso pegando o email e exlcuindo a foto antiga!
        cursor.execute(""" 
            SELECT foto_de_perfil FROM Pessoas
            where email = ?""",(email,))
        foto_excluir = cursor.fetchone()[0]
        try:
            remove(path.join(getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usarios' + f'\\{foto_excluir}')) # Para remover o arquivo!
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        # Colocando a foto no caminho certo, verificação de id
        id_da_pessoa = Pessoas.verificar_id_foto(email) + '_' + foto
        # Alterando os dados, a partir do email, já que é único!
        cursor.execute(""" 
            Update Pessoas
                set 
                nome = ?,
                sexo = ?,
                forma_de_pagamento = ?,
                preferencia = ?,
                foto_de_perfil = ?,
                senha = ?
            where email = ?""",(nome, sexo, forma_de_pagamento, preferencia, id_da_pessoa, senha, email))
        conexao.commit()
        conexao.close()
        return id_da_pessoa
    @staticmethod
    def excluir_ususario(email):
        from os import remove, path, getcwd
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        # exclui a foto de perfil
        cursor.execute(""" 
            SELECT foto_de_perfil FROM Pessoas
            where email = ?""",(email,))
        foto_excluir = cursor.fetchone()[0]
        try:
            remove(path.join(getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usarios' + f'\\{foto_excluir}')) # Para remover o arquivo!
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        # excluir a conta
        cursor.execute(""" 
            DELETE FROM Pessoas
            where email = ?""",(email,))
        conexao.commit()
        conexao.close()

class Produtos:
    @staticmethod
    def adicionar_produto(tipo, nome, descricao, imagem, preco):
        """ 
        Função que adiciona valores ao site!
        Utilização:
        tipo: Existem somente três tipos!
        nome: Escolha o nome do produto
        descricao: Escolha a descrição do produto!
        imagem: Escolha uma imagem que esteja em img/compras! Mande somente o nome dela!
        preco: Digite o preco! O preco tem que ser com '', ou seja, uma string!
        """
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO Produtos(tipo, nome, descricao, imagem, preco) Values
            (?, ?, ?, ?, ?);
            """,(tipo, nome, descricao, imagem, preco))
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
    def add_carrinho(email, idProduto, quantidade):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT idPessoas FROM Pessoas
            where email = ?""",(email,))
        idUsuario = cursor.fetchall()[0][0]
        cursor.execute(""" 
            INSERT INTO Carrinho(idPessoas, produto, quantidade) Values
            (?, ?, ?)""",(idUsuario, idProduto, quantidade))
        conexao.commit() # o PREÇO DO PRODUTO EU SEI A PARTIR DO PRODUTO!
        conexao.close()
    @staticmethod
    def ver_carrinho(email):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT idPessoas FROM Pessoas
            WHERE email = ?""",(email,))
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
                    preco = produtos[5]
                    quantidade = int(carrinho[3])
                    itens = [carrinho[0], produtos[1], produtos[2], produtos[3], produtos[4], preco, quantidade] 
                    carrinho_usuario.append(itens.copy())
                    itens.clear()
                    break
        return carrinho_usuario
    @staticmethod
    def comprar_excluir(status, idCarrinho, email=None, preco=None): 
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        if status == 'comprar':
            cursor.execute("""
                SELECT idPessoas, dinheiro FROM Pessoas
                where email = ?""",(email,))
            dados = cursor.fetchone()
            idPessoas = dados[0]
            dinheiro = dados[1]
            if preco > dinheiro:
                return False
            cursor.execute("""
                Update Pessoas
                set dinheiro = dinheiro - ?
                where idPessoas = ?""",(preco, idPessoas))
            conexao.commit()
            cursor.execute("""
                DELETE FROM Carrinho
                where idCompra = ?""",(idCarrinho,))
            conexao.commit()
            conexao.close()
            return True
        if status == 'excluir':
            cursor.execute("""
                DELETE FROM Carrinho
                where idCompra = ?""",(idCarrinho,))
            conexao.commit()
        conexao.close()
    @staticmethod
    def cookie(email):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT preferencia FROM Pessoas
            where email = ?""",(email,))
        preferencia = cursor.fetchone()[0]
        conexao.close()
        return preferencia
'''conexao = sqlite3.connect("bancodedados.db")
cursor = conexao.cursor()
cursor.execute("""DROP TABLE Pessoas""")
cursor.execute("""DROP TABLE Carrinho""")
cursor.execute("""DROP TABLE Produtos""")
# criando as tabelas
cursor.execute(""" 
    CREATE TABLE Pessoas (
        idPessoas INTEGER PRIMARY KEY NOT NULL,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        sexo TEXT NOT NULL CHECK(sexo IN ('M', 'F')),
        foto_de_perfil TEXT NOT NULL,
        forma_de_pagamento TEXT NOT NULL,
        preferencia TEXT NOT NULL,
        senha TEXT NOT NULL,
        dinheiro FLAOT NOT NULL
        );
    """)
cursor.execute(""" 
    CREATE TABLE Carrinho(
        idCompra INTEGER PRIMARY KEY NOT NULL,
        idPessoas INTEGER NOT NULL,
        produto INTEGER NULL,
        quantidade FLOAT NOT NULL
        );
    """)
cursor.execute(""" 
    CREATE TABLE Produtos(
        idProdutos INTEGER PRIMARY KEY NOT NULL,
        tipo TEXT NOT NULL,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL,
        imagem TEXT NOT NULL,
        preco TEXT NOT NULL
        );""")
conexao.close()'''
'''Produtos.adicionar_produto(tipo='doces_quadrados' ,nome='Macarron', descricao='Macarrão bonito de comer', imagem="macarron.jpg", preco='7,20')
Produtos.adicionar_produto(tipo='doces_frescos', nome='Hambúrgueres Doces', descricao='Hambúrgueres doces! Coma e viva!', imagem="docesham.jpg", preco='10,30')
Produtos.adicionar_produto(tipo='doces_epicos', nome="Bolo de Pote", descricao="Um bolo delecioso! Super racheado em um mini formato.", imagem="bolodepote.jpg", preco="14,00")'''

'''conexao = sqlite3.connect("bancodedados.db")
cursor = conexao.cursor()
cursor.execute("SELECT * FROM Pessoas")
print(cursor.fetchall())
conexao.close()'''
#conexao.close()


# quando eu for comprar ele pega o id do usuário e nome do produto, e assim ele altera a quantidade, se caso o nome não existir, ele cria e coloca a quantidade desejada.

# ele vai compras, e vai verificar se a compra com aquele produto existe, se existir ele adiciona mais um, se não, ele cria e adiciona um.
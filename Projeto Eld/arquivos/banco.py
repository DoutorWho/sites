from os import stat
import sqlite3
if __name__ == '__main__':
    conexao = sqlite3.connect("bancodedados.db")
    cursor = conexao.cursor()

class Pessoas:    
    @staticmethod
    def logar(email, senha):
        print("accesei aqui")
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT nome, senha FROM Pessoas 
        where email = ?;""",(email,))
        nome = cursor.fetchall() 
        conexao.close()
        print(nome)
        if nome == []:
            return [False, 'usuário não existe'] # 1 de usuário não existe

        senha_cadastrada = nome[0][1]
        if senha_cadastrada == senha:
            return [True, nome[0][0]]

        return [False, 'senha inválida'] # 2 de senha inválida!
    @staticmethod
    def adicionar_usuario(nome, email, sexo, senha):
        nome = str(nome).title() # para deixar bonito!
        if sexo == 'Masculino':
            sexo = 'M'
        else:
            sexo = 'F'
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        print("cadastrando 1")
        cursor.execute("""
            SELECT * FROM Pessoas
            where email = ?""", (email,))
        email_cadastrado = cursor.fetchall()
        if email_cadastrado == []: # Se isso for igual, é pq não existe email cadastado!
            cursor.execute("""
                           INSERT INTO Pessoas(nome, email, sexo, senha, dinheiro) Values
                           (?, ?, ?, ?, 2000)""",(nome, email, sexo, senha))
            conexao.commit()
            conexao.close()
            return True
        return False


class Produtos:
    @staticmethod
    def adicionar_produto(nome, descricao, imagem, preco):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO Produtos(nome, descricao, imagem, preco) Values
            (?, ?, ?, ?);
            """,(nome, descricao, imagem, preco))
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
    def add_carrinho(email, idProduto, preco, quantidade):
        conexao = sqlite3.connect("bancodedados.db")
        cursor = conexao.cursor()
        cursor.execute(""" 
            SELECT idPessoas FROM Pessoas
            where email = ?""",(email,))
        idUsuario = cursor.fetchall()[0][0]
        cursor.execute(""" 
            INSERT INTO Carrinho(idPessoas, produto, preco, quantidade) Values
            (?, ?, ?, ?)""",(idUsuario, idProduto, preco, quantidade))
        conexao.commit()
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
        carrinho = cursor.fetchall()
        cursor.execute("SELECT * FROM Produtos")
        produtos = cursor.fetchall()
        produtos_carrinho = []
        for produto in produtos: # onde estão os produtos
            produtos_carrinho.append([produto[1], produto[2], produto[3]])
        print("Produtos do carrinho: ",produtos_carrinho)
        for posicao, produto in enumerate(carrinho): # adicionar ao final os preco e a quantidade
            produtos_carrinho[posicao].append([produto[3], produto[4]])
    

        return produtos_carrinho
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
        senha TEXT NOT NULL,
        dinheiro FLAOT NOT NULL
        );
    """)
cursor.execute(""" 
    CREATE TABLE Carrinho(
        idCompra INTEGER PRIMARY KEY NOT NULL,
        idPessoas INTEGER NOT NULL,
        produto TEXT NULL,
        preco FLAOT NOT NULL,
        quantidade FLOAT NOT NULL
        );
    """)
cursor.execute(""" 
    CREATE TABLE Produtos(
        idProdutos INTEGER PRIMARY KEY NOT NULL,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL,
        imagem TEXT NOT NULL,
        preco TEXT NOT NULL
        );""")
'''
'''Produtos.adicionar_produto('Macarron', descricao='Macarrão bonito de comer', imagem="macarron.jpg", preco='7,20')
Produtos.adicionar_produto('Hambúrgueres Doces', descricao='Hambúrgueres doces! Coma e viva!', imagem="docesham.jpg", preco='10,30')'''

'''conexao = sqlite3.connect("bancodedados.db")
cursor = conexao.cursor()
cursor.execute("SELECT * FROM Pessoas")
print(cursor.fetchall())
conexao.close()'''

#Produtos.adicionar_produto(nome="Bolo de Pote", descricao="Um bolo delecioso! Super racheado em um mini formato.", imagem="bolodepote.jpg", preco="14,00")
#Produtos.adicionar_produto('Kit Macaron', "Compre e se divirta!", "lojadedoces.jpg", 10)

# quando eu for comprar ele pega o id do usuário e nome do produto, e assim ele altera a quantidade, se caso o nome não existir, ele cria e coloca a quantidade desejada.

# ele vai compras, e vai verificar se a compra com aquele produto existe, se existir ele adiciona mais um, se não, ele cria e adiciona um.
from time import sleep
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, sessions, url_for
import banco
app = Flask(__name__, template_folder='front_end', static_folder='front_end')
app.secret_key = "legal"
'''conexao = sqlite3.connect("lojadedoces.db")
cursor = conexao.cursor()'''

@app.route("/")
def paginainicial():
    usuario = session.get('usuario', None)
    lista = banco.Produtos.lista_produtos()
    return render_template("pagina_inicial.html", usuario=usuario, produtos=lista)

@app.route("/cadastro")
def cadastro():
    mensagem_erro_cadastro = session.get('mensagem_cadastro')
    mensagem_erro_login = session.get('mensagem_login')
    session.pop("mensagem_cadastro", None)
    session.pop("mensagem_login", None)
    return render_template("cadastro.html", mensagem_erro_cadastro=mensagem_erro_cadastro, mensagem_erro_login=mensagem_erro_login)

@app.route("/carrinho")
def carrinho():
    verificar = session.get('usuario', None)
    if verificar == None:
        return redirect(url_for("erro", tipo_de_erro='Você ainda não se cadastrou!'))
    # vendo os produtos do carrinho
    email = session.get('email')
    lista = banco.Produtos.ver_carrinho(email)
    #
    return render_template("carrinho.html", lista=lista)

@app.route("/erro/<tipo_de_erro>")
def erro(tipo_de_erro):
    print("cheguei aqui")
    print("O tipo é: ", tipo_de_erro)
    return render_template("erros.html", erro=tipo_de_erro)


@app.route("/<pagina>/")
def paginas(pagina):
    if pagina == 'pagina_inicial':
        return redirect(url_for("paginainicial"))
    elif pagina == 'sobre':
        return render_template("sobre.html")
    elif pagina == "historiadaloja":
        return render_template("sobre.html")
    return render_template("erros.html",erro='página inválida')

# pegando as informações
@app.route('/cadastro/submit_form', methods=['post'])
def submit():
    nome = request.form['nome']
    sexo = request.form['sexo']
    email = request.form['email']
    senha = request.form['senha']
    confirmasenha = request.form['confirmasenha']
    if senha != confirmasenha: # se a senha não for igual!
        session['mensagem_cadastro'] = 'Senha inválida! As senhas não são iguais'
        return redirect(url_for("cadastro"))
    # se caso a senha for verdadeira
    resposta = banco.Pessoas.adicionar_usuario(nome, email, sexo, senha) # aqui para adicionar a pessoa!
    if resposta: # se for verdadeiro é pq o email ainda não foi cadastrado!
        session['usuario'] = nome # o nome do usuário para já cadastrar!
        session['email'] = email
        return redirect(url_for("paginainicial"))
    session.pop("mensagem_cadastro", None) # aqui para apagar a mensagem de erro!
    return redirect(url_for("paginainicial"))

@app.route("/login/submit_form", methods=['post'])
def submita():
    email = request.form['email']
    senha = request.form['senha']
    resposta = banco.Pessoas.logar(email, senha)
    if resposta[0]: # Se tudo tiver certo é aprovado aqui na hora!
        session['email'] = email
        session['usuario'] = resposta[1] # que é a que tem o nome do usuário 
        return redirect(url_for("paginainicial"))
    session['mensagem_login'] = resposta[1]
    return redirect(url_for("cadastro"))

@app.route("/addcarrinho/submit_form", methods=['post', 'GET'])
def add_carrinho():
    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])
        preco = float(request.form['preco'].replace(',','.'))
        produto = int(request.form['idProduto'])
        email = session.get('email')
        banco.Produtos.add_carrinho(email=email, idProduto=produto, preco=preco, quantidade=quantidade)
        return redirect(url_for('carrinho'))
        #return f"A quantidade: {quantidade} o preco {preco}, total {quantidade * preco}"
    return redirect(url_for('paginainicial'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)

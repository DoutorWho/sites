import os
from flask import Flask, make_response, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import banco
app = Flask(__name__, template_folder='front_end', static_folder='front_end')
app.secret_key = "legal"
diretorio_imagens = os.path.join(os.getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usarios') 
@app.route("/")
def paginainicial():
    usuario = session.get('usuario', None)
    lista = banco.Produtos.lista_produtos()
    email = session.get("email", None)
    preferencia = request.cookies.get("preferencia", None) 
    if email != None:
        resposta = banco.Produtos.cookie(email)
        resp = make_response(render_template("pagina_inicial.html", usuario=usuario, produtos=lista, preferencia=resposta))
        resp.set_cookie("preferencia", resposta)
        return resp
    return render_template("pagina_inicial.html", usuario=usuario, produtos=lista, preferencia=preferencia)

@app.route("/erro/<tipo_de_erro>")
def erro(tipo_de_erro):
    print("O tipo é: ", tipo_de_erro)
    return render_template("erros.html", erro=tipo_de_erro)

@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST': # Aqui é quando ele entra no cadastro/login! Primeiro, ou seja, POST!
        status = request.form['status']
        return render_template("cadastro.html", status=status)
    else: # se ele é do tipo GET. Ou seja, ou é a segunda vez por erro ou o usuário tá trolando!
        email =  session.get("email")
        mensagem_erro_cadastro = session.get('mensagem_cadastro')
        mensagem_erro_login = session.get('mensagem_login')
        session.pop("mensagem_cadastro", None)
        session.pop("mensagem_login", None)
        if email != None: # Aqui é se ele estiver trolando, isso já resolve!
            return redirect(url_for("erro", tipo_de_erro="Você já está logado!"))
        if (mensagem_erro_cadastro != None): # Aqui é se caso haja uma mensagem de erro!
            return render_template("cadastro.html", mensagem_erro_cadastro=mensagem_erro_cadastro, status='cadastro')
        if (mensagem_erro_login != None): #Aqui é se caso haja uma mensagem de erro!
            return render_template("cadastro.html", mensagem_erro_login=mensagem_erro_login, status='login')
        return redirect(url_for("paginainicial"))

@app.route("/perfil")
def perfil():
    email = session.get("email")
    if email != None:
        resultados = banco.Pessoas.perfil(email) # entrar no banco de dados e pegar os dados!
        status = session.get("status", None)
        session.pop("status", None)
        return render_template("perfil.html", status=status, usuario=resultados[0], email=resultados[1], sexo=resultados[2], imagem=resultados[3], forma=resultados[4], preferencia=resultados[5], dinheiro=resultados[6])
    return redirect(url_for("erro", tipo_de_erro='Você precisa criar uma conta ou entrar na sua!'))

@app.route("/carrinho")
def carrinho():
    verificar = session.get('usuario', None)
    if verificar == None:
        return redirect(url_for("erro", tipo_de_erro='Você ainda não se cadastrou!'))
    # vendo os produtos do carrinho
    email = session.get('email')
    lista = banco.Produtos.ver_carrinho(email)
    status = session.get("compras", None) # Aqui é se tá comprado ou excluido!
    usuario = session.get("usuario", None)
    session.pop("compras", None)
    return render_template("carrinho.html", lista=lista, status=status, usuario=usuario)

@app.route("/<pagina>/")
def paginas(pagina):
    if pagina == 'pagina_inicial':
        return redirect(url_for("paginainicial"))
    elif (pagina == "historiadaloja") or (pagina == 'sobre'):
        usuario = session.get("usuario", None)
        return render_template("sobre.html", usuario=usuario)
    elif pagina == 'perfil':
        return redirect(url_for("perfil"))
    elif pagina == "favicon.ico":
        return "teste" # isso aqui é caso ele tente acessar uma rota já existente, como /cadastro, /carrinho
    return redirect(url_for("erro",tipo_de_erro='página inválida'))

# pegando as informações
@app.route('/cadastro/submit_form', methods=['post'])
def submit():
    nome = request.form['nome']
    sexo = request.form['sexo']
    email = request.form['email']
    forma_de_pagamento = request.form['forma_de_pagamento']
    preferencia = request.form['preferencia']
    foto_de_perfil = request.files['foto']
    senha = request.form['senha']
    confirmasenha = request.form['confirmasenha']
    formato = foto_de_perfil.content_type.split("/")[1]
    if formato not in ['jpeg', 'png']:
        session['mensagem_cadastro'] = 'Erro, digite um arquivo jpeg ou png!'
        return redirect(url_for("cadastro"))
    if senha != confirmasenha: # se a senha não for igual!
        session['mensagem_cadastro'] = 'Senha inválida! As senhas não são iguais'
        return redirect(url_for("cadastro"))
    # Aqui é o id da Pessoa onde a foto será adicionada!
    foto = banco.Pessoas.verificar_id_foto() + '_' +  str(foto_de_perfil.filename)  # Aqui é o seguinte, ele vai retornar o id do usuário e adiciona o nome da foto! Para a gente saber a qual id pessoa a foto!
    SaveFoto = os.path.join(diretorio_imagens, secure_filename(foto)) #aqui vai ficar o diretório e o id da foto. Este "_" é para eu saber onde termina o id!
    resposta = banco.Pessoas.adicionar_usuario(nome, email, sexo, foto, forma_de_pagamento, preferencia, senha) # aqui para adicionar a pessoa! E a foto!
    foto_de_perfil.save(SaveFoto) # para salvar a foto
    # se caso a senha for verdadeira
    if resposta: # se for verdadeiro é pq o email ainda não foi cadastrado!
        session['usuario'] = nome # o nome do usuário para já cadastrar!
        session['email'] = email
        session.pop("mensagem_cadastro", None) # aqui para apagar a mensagem de erro!
        return redirect(url_for("paginainicial"))
    session['mensagem_cadastro'] = 'Esse email já existe!'
    return redirect(url_for("cadastro"))

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
        produto = int(request.form['idProduto'])
        email = session.get('email')
        banco.Produtos.add_carrinho(email=email, idProduto=produto, quantidade=quantidade)
        return redirect(url_for('carrinho'))
    return redirect(url_for('paginainicial'))

@app.route("/carrinhoform/submit_form", methods=['post', 'GET'])
def carrinho_compra_excluir():
    if request.method == 'POST':
        idCarrinho = request.form['idCarrinho']
        comprar = request.form.get("comprar")
        excluir = request.form.get("excluir")
        if comprar != None:
            preco = request.form['preco']
            quantidade = request.form['quantidade']
            email = session.get("email")
            total = float(preco.replace(',','.')) * float(quantidade) # Aqui é o total que ele vai pagar!
            retorno = banco.Produtos.comprar_excluir(status='comprar', idCarrinho=idCarrinho, email=email, preco=total)
            if not retorno: # Ou seja, se ele for falso significa que a pessoa tá pobre!
                session['compras'] = 'sem_dinheiro'
                return redirect(url_for("carrinho"))
            print("Passei aqui!")
            session['compras'] = 'compra_sucesso'
            return redirect(url_for("carrinho"))
        if excluir != None:
            banco.Produtos.comprar_excluir(status='excluir', idCarrinho=idCarrinho)
            session['compras'] = 'excluido'
            return redirect(url_for("carrinho"))
    return redirect(url_for("erro", tipo_de_erro="Página não encontrada!"))

@app.route("/alterar_perfil/submit_form", methods=['POST', 'GET'])
def perfil_status():
    tipo = request.form['tipo']
    if request.method == 'POST':
        if tipo == 'normal': # Isso quer dizer que ele quer alterar a conta!
            status = request.form['status_conta'] #Aqui é para verificar o que fazer no inicio
            session['status'] = status # Isso pra certificar lá na rota perfil! Pra ele passar!
            if status == 'alterar':
                return redirect(url_for("perfil"))
            if status == 'excluir':
                email = session['email']
                banco.Pessoas.excluir_ususario(email)
                session.clear()
                return redirect(url_for("paginainicial"))
            if status == 'sair':
                session.clear()
                return redirect(url_for("paginainicial"))
        if tipo == 'novo_perfil':
            nome = request.form['nome']
            sexo = request.form['sexo']
            forma_de_pagamento = request.form['forma_de_pagamento']
            preferencia = request.form['preferencia']
            foto = request.files['foto']
            senha = request.form['senha']
            email = session['email']
            formato = foto.content_type.split("/")[1]
            if formato not in ['jpeg', 'png']: 
                session['status'] = 'Erro, digite um arquivo jpeg ou png!'
                return redirect(url_for("perfil"))
            nome_foto = str(foto.filename)
            foto_do_perfil = banco.Pessoas.alterar_ususario(email=email, nome=nome, sexo=sexo, forma_de_pagamento=forma_de_pagamento, preferencia=preferencia, foto=nome_foto, senha=senha)
            SaveFoto = os.path.join(diretorio_imagens, secure_filename(foto_do_perfil))
            foto.save(SaveFoto)
            session['status'] = 'alterar_sucesso'
            session['usuario'] = nome
        return redirect(url_for("perfil"))
    return ''
if __name__ == "__main__":
    app.run(debug=True, port=5000)

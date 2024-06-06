import os
from random import randint
import secrets
import json
from flask import Flask, make_response, render_template, request, redirect, session, sessions, url_for, abort
from werkzeug.utils import secure_filename
import banco
app = Flask(__name__, template_folder='front_end', static_folder='front_end')
app.secret_key = "7bd6889de3d82f03dfdf90b18e9435e9036ec428"
diretorio_imagens = os.path.join(os.getcwd() + '\\arquivos' + '\\front_end' + '\\imagens_usuarios') 


# tratamento de erros
@app.errorhandler(403)
def acesso_nao_autorizado(erro):
    return render_template("erros.html", erro=erro.description, codigo=erro.code), 404

@app.errorhandler(404)
def pagina_nao_encontrada(erro): # Isso aqui ele recebe um HTTPException, que é como o tratamento de erro
    return render_template("erros.html", erro=erro.description, codigo=erro.code), 404

@app.errorhandler(401)
def login_ou_cadastro_mal_realizado(erro):
    return render_template("erros.html",erro=erro.description), 401

@app.errorhandler(406)
def resposta_nao_permetida(erro):
    return render_template("erros.html",erro=erro.description), 406

# código normal
@app.route("/")
def paginainicial():
    nome_usuario = session.get('nome_usuario', None)
    lista = banco.Produtos.lista_produtos()
    cpf = session.get("cpf", None)
    avaliacao = banco.Produtos.ver_avaliacao() # sem parâmetro significa que ele vai pegar todos as avaliações
    if cpf != None:
        informacao_cookies = request.cookies.get("preferencia", None) # não tem isso de saída de dados, é só preferência!
        if informacao_cookies != None:
            preferencia = json.loads(informacao_cookies)
            dados = banco.Pessoas.pegar_cookie(preferencia)
        else:
            dados = None
        #{'Acessos': {}, 'Tipos_produtos': {} }
        return render_template("pagina_inicial.html", usuario=nome_usuario, produtos=lista, avaliacao=avaliacao, dados=dados, len=len)
    return render_template("pagina_inicial.html", usuario=nome_usuario, produtos=lista, avaliacao=avaliacao, dados=None, len=len)


@app.route("/produto/<nome_produto>/<id_do_produto>")
def produto(nome_produto, id_do_produto): # controlar pra produtos desconhecidos depois!
    session['site_produto'] = f"{nome_produto}/{id_do_produto}"
    lista = banco.Produtos.produtos_descricao(nome_produto=nome_produto, id_produto=id_do_produto)
    if lista[0] == 'Erro': # aqui  ele verifica se o usuário tá entrando em uma página que não existe!
        return abort(404, description='Página não encontrada!')

    avaliacao = banco.Produtos.ver_avaliacao(int(id_do_produto))
    comentarios = banco.Comentario.ver_comentarios(int(id_do_produto)) 
    comentario_principal = comentarios[0]
    resposta_comentario = comentarios[1]
    visto = request.args.get("visto", None)
    idNotificacao = request.args.get("idNotificacao", None)
    nome_usuario = session.get('nome_usuario', None)
    nome_perfil = '@' + session.get("nome_perfil", 'a') # aqui é pra não da erro na lista
    if (visto != None) and (idNotificacao != None):
        banco.Pessoas.tirar_notifacoes(nome=nome_perfil.replace('@',''), visto=visto, idNotificacao=idNotificacao) # resolver isso!

    # aqui é pra fazer o cookie pegar!
    cpf = session.get("cpf", None)
    if cpf != None:
        cookies = request.cookies.get("preferencia", None)
        if cookies == None:
            # criando o cookie de preferência
            preferencia = make_response(render_template("produtos_detalhes.html", produto=lista, avaliacao=avaliacao, nome_perfil=nome_perfil, usuario=nome_usuario, comentario_principal=comentario_principal, resposta_comentario=resposta_comentario)) 
            cookie_resposta = json.dumps({'Acessos': {}, 'Tipos_produtos': {} }, ensure_ascii=False) # Dicionários com os nomes e quantidades de acessos!
            preferencia.set_cookie('preferencia', cookie_resposta)
            return preferencia
        else:
            cookies = request.cookies["preferencia"]
            cookies_atualizado = json.loads(cookies)
            informacao_entrada = [nome_produto, id_do_produto] # o erro tá aqui pq vou atualizando isso, aí fica criando vários
            resposta = banco.Pessoas.enviar_cookie(informacao_entrada=informacao_entrada, cookies=cookies_atualizado) # pq ele vai pegar os dados! 
            cookie_resposta = json.dumps(resposta, ensure_ascii=False) 
            preferencia = make_response(render_template("produtos_detalhes.html", produto=lista, avaliacao=avaliacao, nome_perfil=nome_perfil, usuario=nome_usuario, comentario_principal=comentario_principal, resposta_comentario=resposta_comentario)) 
            preferencia.set_cookie("preferencia", cookie_resposta) #criando um novo cookie de mesmo nome pra autilizar os dados
            cookies = request.cookies["preferencia"] #{"Acessos": {"Hambúrgueres Doces": 3, "Torta de Limão": 4}, "Tipos_produtos": {"doces_frescos": 3, "doces_relaxantes": 4}}       
            return preferencia

    return render_template("produtos_detalhes.html", produto=lista, avaliacao=avaliacao, nome_perfil=nome_perfil, usuario=nome_usuario, comentario_principal=comentario_principal, resposta_comentario=resposta_comentario)

@app.route("/perfil", defaults={'usuario_perfil': 'meu_perfil'})
@app.route("/perfil/<usuario_perfil>")
def perfil(usuario_perfil):
    nome_perfil = session.get('nome_perfil', None)
    if nome_perfil != None: # Ou seja, se ele tiver uma conta!
        usuario_perfil = usuario_perfil.lower().replace("@",'') # Isso é pra evitar os @ e os nomes maiúsculo!
        # status é um parâmetro pra descobrir se ele quer alterar, a conta, excluir, essas coisas!
        if (usuario_perfil == nome_perfil): # aqui é se o perfil que ele tá tentando acessar é o dele
            return redirect(url_for("perfil", usuario_perfil='meu_perfil'))

        if usuario_perfil == 'meu_perfil': # aqui é se o perfil for dele! Aí ele pode alterar, etc!
            session['token'] = secrets.token_hex(15)
            token = session.get('token')
            resultados = banco.Pessoas.perfil(perfil_do_usuario=nome_perfil, perfil_status='proprio') # entrar no banco de dados e pegar os dados! Do usuário no 
            dados = resultados[0]
            imagem = resultados[1]
            status_perfil = session.get("status", None) # Aqui é pra saber a parte de alterar a conta ou não! 
            erro = session.get('erro_perfil', None)
            session.pop('erro_perfil', None)
            session.pop("status", None) # true quer dizer que é meu perfil e false quer dizer que não é, no status!
            usuario = session.get('nome_perfil', None)
            return render_template("perfil.html", status=True, status_perfil=status_perfil, usuario=usuario, informacoes_usuarios=dados, erro_perfil=erro, imagem=imagem, parte='perfil', token=token, len=len)
        cpf = session.get("cpf", None)
        resultados = banco.Pessoas.perfil(perfil_do_usuario=usuario_perfil, perfil_status='outro', meucpf=cpf) # entrar no banco de dados e pegar os dados!  Resolver a para do Maisuclo e Minisculo. Capatilaze o sistemas e não permite que o usuário coloque _. | Problema resolvido.
        dados = resultados[0]
        if resultados[0] == 'erro':
            return abort(401, description="Este usuário não existe ou ele apagou a conta!")
        imagem = resultados[1]
        return render_template("perfil.html", status=False, status_perfil=None, informacoes_usuarios=dados, imagem=imagem, parte='perfil', usuario=nome_perfil, len=len)
    return abort(401, description="Você precisa criar uma conta ou entrar na sua para acessar perfil alheios ou entrar no seu!")

@app.route("/notificacoes")
def notificacoes():
    token_url = request.args.get('token', None)
    token = session.get("token", None)
    session.pop('token', None) # usar variáveis, aquela com ? pra pegar a mensagem e colocar como visto!
    if token == token_url:
        nome_perfil = session.get("nome_perfil", None)
        nome_usuario = session.get("nome_usuario", None)
        perfil = banco.Pessoas.perfil(perfil_do_usuario=nome_perfil, perfil_status='meu')[0] #type: ignore
        return render_template("notificacoes.html", usuario=nome_usuario, mensagens=perfil)
    return abort(403, description="Página não encontrada!")


@app.route("/carrinho")
def carrinho():
    verificar = session.get('cpf', None)
    if verificar == None:
        return abort(406, description="Você ainda não se cadastrou!")
    # vendo os produtos do carrinho
    cpf = session.get('cpf', None)
    lista = banco.Produtos.ver_carrinho(cpf)
    status = session.get("compras", None) # Aqui é se tá comprado ou excluido!
    nome_perfil = session.get("nome_perfil", None) 
    session.pop("compras", None)
    resultados = banco.Pessoas.perfil(perfil_do_usuario=nome_perfil, perfil_status='meu_usuario')[1] # entrar no banco de dados e pegar a imagem!
    informacoes_usuarios = {}
    nome_usuario = str(session.get("nome_perfil", 'None')).replace("@", '')
    informacoes_usuarios['nome'] = nome_usuario # Aqui é lá na parte de nav, pra aparecer!
    return render_template("carrinho.html", lista=lista, status=status, usuario=nome_usuario, imagem=resultados, informacoes_usuarios=informacoes_usuarios)

@app.route("/compras", defaults={'status': 'visualizacao'})
@app.route("/compras/<status>")
def compras(status):
    # fazer a verificação pra quem não cadastrado não conseguir entrar
    cpf_verificar = session.get('cpf', None)
    if cpf_verificar == None:
        return abort(406, description="Você ainda não se cadastrou!")
    # código para quem é cadastrado
    if status == 'comprar-produto':
        dados = request.cookies.get('arquivos_compras', None)
        if dados == None: # Se os dados estiverem vazios
            return abort(406, description="Acesso não autorizado!")
        else: # caso os dados estejam com conteúdo
            dados = json.loads(dados)
            quantidade = len(dados['produtos'])
            compras = make_response(render_template("compras.html", status='compra_de_produto', informacao=dados, quantidade=quantidade))
            compras.set_cookie('arquivos_compras', '', expires=0)
            return compras
    if status == 'pagamento-pix':
        pagamento_status = session.get('pagamento_status', None)
        session.pop("pagamento_status", None) # isso garante que ele não entra nessa página denovo
        pagamento_token = request.args.get("token", None)
        if (pagamento_status != None) and (pagamento_status == pagamento_token): # tem ser != None pq ele pode colocar os dois None
            # colocar um parâmetro para o usuário não gerar toda hora uma chave pix!
            chave = session['todos_dados_pix'][2]
            return render_template("compras.html", status='pagamento-pix', informacao={'chave_pix': chave})
    if status == 'pagamento': # caso o apgamento esteja em orem
        chave = session.get('todos_dados_pix', ['None']) #['100', "{'produtos': ['Bolo de Pote'], 'idCarrinhos': ['1'], 'quantidades_totais': ['5'], 'precos_totais': ['14'], 'frete': '3.78', 'imagem': ['bolodepote.jpg'], 'totalpago': '70,00'}", '8b935b92d21b0d10d41afb32298ccc7bce5fad35'] coloquei uma lista ali pra parar aquela mensagem chato embaixo!
        if chave == ['None']:
            abort(404, description="Página não encontrada.")   
        session.pop('todos_dados_pix', None)
        session.pop("chave_pix", None)
        banco.Compra.pagamento(chave_pix=chave[2], dados=chave[0:2])
        return '<h1>Pagamento Efetuado com sucesso!</h1>'

    if status == 'pagamento-cartao':
        pagamento_status = session.get('pagamento_status', None)
        pagamento_token = request.args.get("token", None)
        session.pop("pagamento_status", None)
        if (pagamento_status != None) and (pagamento_status == pagamento_token):
            return "Compra no cartão de crédito realizada com sucesso!"
    cpf = session.get('cpf', None)
    lista = banco.Compra.compras_status(cpf=cpf, produtos=banco.Produtos.lista_produtos())
    usuario = session.get("nome_usuario", None)
    return render_template("compras.html", status='visualizacao', compras=lista, usuario=usuario, len=len)

@app.route("/<pagina>/")
def paginas(pagina):
    if (pagina == 'pagina_inicial') or (pagina == 'home'):
        return redirect(url_for("paginainicial"))
    elif (pagina == "historiadaloja") or (pagina == 'sobre'):
        nome_usuario = session.get("nome_usuario", None)
        return render_template("sobre.html", usuario=nome_usuario)
    elif (pagina == 'perfil') or (pagina == 'usuario'):
        return redirect(url_for("perfil"))
    elif (pagina == 'compras') or (pagina == 'compra'):
        return redirect(url_for("compras"))
    return abort(404, description="Página não encontrada.")



# pegando as informações
@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST': # Aqui é quando ele entra no cadastro/login! Primeiro, ou seja, POST!
        status = request.form['status']
        return render_template("cadastro.html", status=status)
    else: # se ele é do tipo GET. Ou seja, ou é a segunda vez por erro ou o usuário tá trolando!
        cpf =  session.get("cpf")
        mensagem_erro_cadastro = session.get('mensagem_cadastro')
        mensagem_erro_login = session.get('mensagem_login')
        session.pop("mensagem_cadastro", None)
        session.pop("mensagem_login", None)
        if cpf != None: # Aqui é se ele estiver trolando, isso já resolve!
            return abort(406, description="Você já está logado!")
        if (mensagem_erro_cadastro != None): # Aqui é se caso haja uma mensagem de erro!
            return render_template("cadastro.html", mensagem_erro_cadastro=mensagem_erro_cadastro, status='cadastro')
        if (mensagem_erro_login != None): #Aqui é se caso haja uma mensagem de erro!
            return render_template("cadastro.html", mensagem_erro_login=mensagem_erro_login, status='login')
        return redirect(url_for("paginainicial"))

@app.route('/cadastro/submit_form', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        nome_perfil = request.form['nome_perfil']
        nome_usuario = request.form['nome_usuario']
        cpf = request.form['cpf']
        sexo = request.form['sexo']
        email = request.form['email']
        cidade = request.form['cidade']
        foto_de_perfil = request.files['foto_de_perfil']
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
        resposta = banco.Pessoas.adicionar_usuario(nome_perfil=nome_perfil, nome_usuario=nome_usuario, cpf=cpf, email=email, sexo=sexo, cidade=cidade, foto_de_perfil=foto, senha=senha) # aqui para adicionar a pessoa! E a foto!
        # se caso a senha for verdadeira
        if resposta[0]: # se for verdadeiro é pq o email ainda não foi cadastrado!
            foto_de_perfil.save(SaveFoto) # para salvar a foto. No caso ele só salva se o email não for cadastrado ainda!
            session['nome_usuario'] = nome_usuario # o nome do usuário!
            session['nome_perfil'] = nome_perfil # o @ do usuário no caso!
            session['cpf'] = cpf # aqui é o cpf, para eu testar alguns funções
            session.pop("mensagem_cadastro", None) # aqui para apagar a mensagem de erro!
            return redirect(url_for("paginainicial"))
        session['mensagem_cadastro'] = resposta[1]
        return redirect(url_for("cadastro"))
    return abort(404, description="Página não encontrada!")

@app.route("/login/submit_form", methods=['post', 'get'])
def submita():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        resposta = banco.Pessoas.logar(email, senha)
        if resposta[0]: # Se tudo tiver certo é aprovado aqui na hora!
            session['nome_usuario'] = resposta[1] # que é a que tem o nome do usuário 
            session['nome_perfil'] = resposta[2] # o @ do usuário no caso!
            session['cpf'] = resposta[3]
            return redirect(url_for("paginainicial"))
        session['mensagem_login'] = resposta[1]
        return redirect(url_for("cadastro"))
    return abort(404, description="Página não encontrada!")

@app.route("/addcarrinho/submit_form", methods=['post', 'GET'])
def add_carrinho():
    if request.method == 'POST':
        cpf = session.get('cpf', None)
        if cpf != None: # Aqui é pra verificar o seguinte, se ele tiver email, essa parte não da erro, se caso ele não tiver da erro!
            quantidade = int(request.form['quantidade'])
            produto = int(request.form['idProduto'])
            banco.Produtos.add_carrinho(cpf=cpf, idProduto=produto, quantidade=quantidade)
            return redirect(url_for('carrinho'))
        return abort(406, description="Você precisa ser cadastrado para realizar uma compra!")
    return abort(404, description="Página não encontrada!")


@app.route("/comprarprodutoform/submit_form", methods=['post', 'GET'])
def carrinho_compra_excluir():
    if request.method == 'POST':
        status = request.form['status'] # aqui é pra saber se ele quer comprar ou excluir
        if status == 'comprar':
            produtos = request.form['nome-produtos'].split(',') # ['a', 'a']
            idCarrinho = request.form['carrinho-produtos'].split(',')
            quantidadeTotal = request.form['quantidade-total'].split(',') 
            precoTotal = request.form['preco-total'].split(',')  
            compras = make_response(redirect(url_for("compras", status="comprar-produto")))
            frete = format(randint(1, 120) / randint(1, 120), '.2f')
            arquivos = banco.Produtos.comprar_excluir(status='comprar', dados={'produtos': produtos, 'idCarrinhos': idCarrinho, 'quantidades_totais': quantidadeTotal, "precos_totais": precoTotal, 'frete': frete})
            arquivos = json.dumps(arquivos, ensure_ascii=False)
            compras.set_cookie("arquivos_compras", arquivos)
            return compras

        if status in ['pix', 'cartao']:
            dados = request.form['dados'].replace("'", "\"") #{'produtos': ['Bolo de Pote'], 'idCarrinhos': ['1'], 'quantidades_totais': ['5'], 'precos_totais': ['14'], 'frete': '6.06', 'imagem': ['bolodepote.jpg'], 'totalpago': '70,00'} 
            verificador = session.get('todos_dados_pix', None) # Aqui é pra não gerar vários json se ele voltar a página!]
            if (status == 'pix') and (verificador == None): # aqui é a garantia
                session['pagamento_status'] = pagamento = secrets.token_hex(10)
                cpf = session.get("cpf")
                dados = json.loads(dados)
                chave_pix = secrets.token_hex(20)
                session['todos_dados_pix'] = [cpf, dados, chave_pix] # status = pagamento_pix ou pagamento_cartao
                banco.Compra.pagamento(status='gerar_pagamento', chave_pix=chave_pix)
                return redirect(url_for("compras", status='pagamento-pix', token=pagamento))
            # pegar os dados do cartão
            verificador = session.get('todos_dados_pix', None) # Aqui é pra não gerar vários json se ele voltar a página!]
            if (status == 'cartao') and (verificador == None):
                dados = json.loads(dados)
                cpf = session.get("cpf")
                banco.Compra.pagamento(dados=[cpf, dados])
                session['pagamento_status'] = pagamento = secrets.token_hex(10)
                return redirect(url_for("compras", status='pagamento-cartao', token=pagamento))
            session.pop("todos_dados_pix", None) # Aqui é pra não gerar vários json se ele voltar a página!
            return redirect(url_for("carrinho"))
        if status == 'excluir':
            idCarrinho = request.form.get('idCarrinho', None)
            idCarrinho = request.form['idCarrinho']
            banco.Produtos.comprar_excluir(status='excluir', idCarrinho=idCarrinho)
            return redirect(url_for("carrinho"))
    return abort(404, description="Página não encontrada!")

@app.route("/alterar_perfil/submit_form", methods=['POST', 'GET'])
def perfil_status():
    if request.method == 'POST':
        tipo = request.form['tipo']
        if tipo == 'normal': # Isso quer dizer que ele quer alterar a conta!
            status = request.form['status_conta'] #Aqui é para verificar o que fazer no inicio
            session['status'] = status # Isso pra certificar lá na rota perfil! Pra ele passar!
            if status == 'alterar':
                return redirect(url_for("perfil"))
            if status == 'excluir':
                cpf = session.get('cpf')
                banco.Pessoas.excluir_ususario(cpf)
                session.clear()
                preferencia = make_response("")
                preferencia.set_cookie("preferencia", expires=0)
                return redirect(url_for("paginainicial"))
            if status == 'sair':
                session.clear()
                preferencia = make_response("")
                preferencia.set_cookie("preferencia", expires=0)
                return redirect(url_for("paginainicial"))
        if tipo == 'novo_perfil':
            nome_usuario = request.form['nome_usuario']
            cidade = request.form['cidade']
            foto = request.files['foto']
            senha = request.form['senha']
            formato = foto.content_type.split("/")[1]
            if formato not in ['jpeg', 'png']: 
                session['status'] = 'Erro, digite um arquivo jpeg ou png!'
                return redirect(url_for("perfil"))
            nome_foto = str(foto.filename)
            cpf = str(session.get("cpf"))
            foto_do_perfil = banco.Pessoas.alterar_ususario(cpf=cpf, nome_usuario=nome_usuario, cidade=cidade, foto=nome_foto, senha=senha)

            if foto_do_perfil == 'Nome já existe': # Isso quer dizer que o nome já existe! Então ele tem que escolher outro!
                print("Gerou o erro!")
                session['erro_perfil'] = 'Esse nome já existe! Por favor, escolha outro.'
                return redirect(url_for("perfil")) 
            SaveFoto = os.path.join(diretorio_imagens, secure_filename(foto_do_perfil))
            foto.save(SaveFoto)
            session['status'] = 'alterar_sucesso'
            session['nome_usuario'] = nome_usuario
        return redirect(url_for("perfil"))
    return abort(404, description="Página não encontrada!")

@app.route("/comentario/submit_form", methods=['POST', 'GET'])
def comentarios():
    if request.method == 'POST':
        cpf = session.get('cpf', None)
        site_produto = session.get("site_produto", None)
        if site_produto != None:
            site_produto = site_produto.split('/')
            nome_id_produto = site_produto
            tipo = request.form['tipo']
            if tipo == 'enviar_mensagem':
                if cpf != None:
                    comentario = request.form['comentario']
                    resposta = request.form['resposta']
                    banco.Comentario.adicionar_comentario(comentario=comentario, idProduto=site_produto[1], remetente=resposta, cpf=cpf, nome_id_produto=nome_id_produto)
                    # adicionar no banco de dados o comentário
                    comentario = request.form['comentario']
                    return redirect(url_for("produto", nome_produto=site_produto[0], id_do_produto=site_produto[1])) # pra redirecionar ele pro site
                return redirect(url_for("produto", nome_produto=site_produto[0], id_do_produto=site_produto[1]))
            elif tipo == 'apagar':
                idComentario = request.form['idComentario']
                banco.Comentario.remover_comentario(idComentario, cpf=cpf)
                return redirect(url_for("produto", nome_produto=site_produto[0], id_do_produto=site_produto[1]))
        return 'aa' # nunca vai ser igual a None isso!
    return redirect(url_for("paginainicial"))

@app.route("/avaliar_produto/submit_form", methods=['POST', 'GEY'])
def avaliacao():
    if request.method == 'POST':
        cpf = session.get('cpf', None)
        site_produto = session.get("site_produto", None)
        if site_produto != None:
            site_produto = site_produto.split('/')
            if cpf != None:
                idProduto = int(request.form['idProduto'])
                avaliacao = request.form['avaliacao']
                nome = request.form['nome_produto']
                banco.Produtos.avaliar_produto(cpf=cpf, idProduto=idProduto, nome=nome, avaliacao=avaliacao)
                return redirect(url_for("produto", nome_produto=site_produto[0], id_do_produto=site_produto[1]))
            return redirect(url_for("produto", nome_produto=site_produto[0], id_do_produto=site_produto[1]))
        return '' # esse nunca vai acontecer!
    return redirect(url_for("pagina_inicial"))

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000) #0.0.0.0

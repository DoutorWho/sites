document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('compra-form');
    if (form) {
        // Adiciona o evento de envio do formulário
        form.addEventListener('submit', function(event) {
            const checkboxes = document.querySelectorAll('.comprar-checkbox');
            let isSelected = false;
            let isValid = true;

            checkboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    isSelected = true;
                    const quantidadeInput = checkbox.previousElementSibling.previousElementSibling;
                    const quantidade = parseInt(quantidadeInput.value);
                    if (quantidade < 1 || quantidade > 20 || isNaN(quantidade)) {
                        isValid = false;
                    }
                }
            });

            if (!isSelected) {
                alert("Por favor, selecione pelo menos um produto antes de enviar o pedido.");
                event.preventDefault(); // Impede o envio do formulário
            } else if (!isValid) {
                alert("Por favor, insira uma quantidade válida (entre 1 e 20) para todos os produtos selecionados.");
                event.preventDefault(); // Impede o envio do formulário
            } else {
                calcularTotal(); // Só calcula o total e prepara para envio se ao menos um produto estiver selecionado
            }
        });

        // Adiciona eventos de entrada nos campos de quantidade
        const quantidadeInputs = document.querySelectorAll('.quantidade-produto');
        quantidadeInputs.forEach(function(input) {
            input.addEventListener('input', calcularTotal);
        });

        // Adiciona eventos de clique nos checkboxes
        const checkboxes = document.querySelectorAll('.comprar-checkbox');
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('click', calcularTotal);
        });
    } else {
        console.error('O formulário de compra não foi encontrado no documento.');
    }
});


function calcularTotal() {
    const checkboxes = document.querySelectorAll('.comprar-checkbox');
    const nomeProdutosInput = document.getElementById('nome-produtos');
    const carrinhoProdutosInput = document.getElementById('carrinho-produtos');
    const quantidadeTotalInput = document.getElementById('quantidade-total');
    const precoTotalInput = document.getElementById('preco-total');

    const produtosElement = document.getElementById('total-produtos');
    const carrinhoElement = document.getElementById('total-valor');

    let totalProdutos = 0;
    let totalValor = 0;
    let nomeProdutosArray = [];
    let carrinhoProdutosArray = [];
    let precosTotalArray = [];
    let quantidadesTotalArray = [];

    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const quantidadeInput = checkbox.previousElementSibling.previousElementSibling;
            const quantidade = parseInt(quantidadeInput.value);
            if (quantidade >= 1 && quantidade <= 20) {
                totalProdutos++;

                // Preços
                const precoInput = checkbox.previousElementSibling;
                const preco = parseFloat(precoInput.value);
                precosTotalArray.push(preco);

                quantidadesTotalArray.push(quantidade);
                totalValor += preco * quantidade;

                // Carrinho dos produtos
                const carrinhoInput = quantidadeInput.previousElementSibling;
                const idCarrinho = carrinhoInput.value;
                carrinhoProdutosArray.push(idCarrinho);

                // Nomes dos produtos
                const nomeProdutoInput = carrinhoInput.previousElementSibling;
                const nomeProduto = nomeProdutoInput.value;
                nomeProdutosArray.push(nomeProduto);
            }
        }
    });

    // Atualize os valores no DOM conforme necessário
    produtosElement.textContent = totalProdutos;
    carrinhoElement.textContent = totalValor.toFixed(2);

    nomeProdutosInput.value = nomeProdutosArray.join(',');
    carrinhoProdutosInput.value = carrinhoProdutosArray.join(',');
    precoTotalInput.value = precosTotalArray.join(',');
    quantidadeTotalInput.value = quantidadesTotalArray.join(',');
}

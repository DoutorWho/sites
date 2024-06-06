window.onload = function() {
    document.querySelectorAll('.detalhes-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            const status = e.target.dataset.status;
            alert(`Status do produto: ${status}`);
        });
    });
};


document.addEventListener('DOMContentLoaded', () => {
    const pagamentoSelect = document.getElementById('pagamento');
    const cartaoInfo = document.getElementById('cartao-info');
    const pixInfo = document.getElementById('pix-info');
    const finalizarCompraButton = document.getElementById('finalizar-compra');
    const statusPagamento = document.getElementById('status');
    
    pagamentoSelect.addEventListener('change', () => {
        const selectedValue = pagamentoSelect.value;
        cartaoInfo.classList.add('hidden');
        pixInfo.classList.add('hidden');
        finalizarCompraButton.disabled = true;

        if (selectedValue === 'cartao') {
            cartaoInfo.classList.remove('hidden');
            statusPagamento.value = 'cartao';
            console.log("Status do pagamento definido como: " + statusPagamento.value);
        } else if (selectedValue === 'pix') {
            pixInfo.classList.remove('hidden');
            statusPagamento.value = 'pix';
            console.log("Status do pagamento definido como: " + statusPagamento.value);
        }

        checkFormValidity();
    });

    const formInputs = document.querySelectorAll('#cartao-info input');
    formInputs.forEach(input => {
        input.addEventListener('input', checkFormValidity);
    });

    function checkFormValidity() {
        const selectedValue = pagamentoSelect.value;
        let isValid = selectedValue !== '';

        if (selectedValue === 'cartao') {
            const numeroCartao = document.getElementById('numero-cartao').value.trim();
            const cvv = document.getElementById('cvv').value.trim();
            const validade = document.getElementById('validade').value.trim();
            isValid = isValid && numeroCartao.length === 16 && cvv.length === 3 && validade.match(/^\d{2}\/\d{2}$/);
        }

        finalizarCompraButton.disabled = !isValid;
    }
});


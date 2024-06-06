function updateStars(value) {
    var stars = '';
    for (var i = 0; i < value; i++) {
        stars += '★ ';
    }
    document.getElementById('stars').textContent = stars;
}

function validateForm() {
    var quantidade = Number(this.elements['quantidade'].value);
    if (quantidade < 1 || quantidade > 20) {
        alert("A quantidade deve ser entre 1 e 20.");
        return false;
    }
    return true;
}

function validateReviewForm(form) {
    var rating = Number(form.elements['avaliacao'].value);
    if (rating <= 0 || rating > 5) {
        alert("A avaliação deve ser entre 1 e 5.");
        return false;
    }
    return true;
}

document.addEventListener('DOMContentLoaded', (event) => {
    var verifiedPurchaseElements = document.querySelectorAll('.verified-purchase');
    verifiedPurchaseElements.forEach(function(element) {
        element.setAttribute('title', 'Compra verificada');
    });

    var produtoAvaliacaoElements = document.querySelectorAll('.produto_avaliacao');
    produtoAvaliacaoElements.forEach(function(element) {
        element.setAttribute('title', 'Avaliação do produto');
    });
});

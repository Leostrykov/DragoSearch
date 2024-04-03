function adjustHTMLForScreenSize() {
    var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    if (width <= 768) {
      // Изменяем атрибут action формы
      var form = document.querySelector('.search_form');
      var label = document.querySelector('.search_input');
      if (form && label) {
        form.action = '/search_mobile';
        form.method = ''
        label.name = ''
      } 
    } else {
        var form = document.querySelector('.search_form');
        var label = document.querySelector('.search_input');
        if (form && label) {
            form.action = '/search';
            form.method = 'get'
            label.name = 'query'
        } 
    }
}

// Вызываем функцию при загрузке страницы
document.addEventListener('DOMContentLoaded', adjustHTMLForScreenSize);

// Вызываем функцию при изменении размера окна
window.addEventListener('resize', adjustHTMLForScreenSize);
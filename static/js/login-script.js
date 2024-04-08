const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});
loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

YaAuthSuggest.init(
    {
       client_id: 'c46f0c53093440c39f12eff95a9f2f93',
       response_type: 'token',
       redirect_uri: 'https://examplesite.com/suggest/token'
    },
    'https://examplesite.com', 
    {
       view: 'button',
       parentId: 'container',
       buttonView: 'main',
       buttonTheme: 'light',
       buttonSize: 'm',
       buttonBorderRadius: 0
    }
 )
 .then(({
    handler
 }) => handler())
 .then(data => console.log('Сообщение с токеном', data))
 .catch(error => console.log('Обработка ошибки', error));

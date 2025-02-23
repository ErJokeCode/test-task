var client_id = Date.now()
var ws = new WebSocket(`ws://localhost:8000/chat/ws/${client_id}`);
var userId = -1

ws.onmessage = function (event) {
    data = JSON.parse(event.data)
    console.log(data)

    if (data.type == 'loading') {
        data.users.forEach(user => {
            if (user.count_not_read != 0) {
                badge = document.createElement('span')
                badge.id = 'notification-' + user.user_id
                badge.className = 'notification-badge'
                badge.textContent = user.count_not_read
                document.getElementById('chat_' + user.user_id).appendChild(badge)
            }
        });
    }
    else if (data.type == 'loadingUser') {
        var badge = document.getElementById('notification-' + data.user.user_id)
        if (badge != null && data.user.count_not_read == 0) {
            badge.remove()
        }
        else if (badge != null) {
            badge.textContent = data.user.count_not_read
        }
        else if (data.user.count_not_read != 0) {
            badge = document.createElement('span')
            badge.id = 'notification-' + data.user.user_id
            badge.className = 'notification-badge'
            badge.textContent = data.user.count_not_read
            document.getElementById('chat_' + data.user.user_id).appendChild(badge)
        }
    }
    else if (data.type == 'notification') {
        var badge = document.getElementById('notification-' + data.user_id)
        if (badge == null) {
            console.log(data.user_id, badge)
            badge = document.createElement('span')
            badge.id = 'notification-' + data.user_id
            badge.className = 'notification-badge'
            badge.textContent = 0
            document.getElementById('chat_' + data.user_id).appendChild(badge)
        }
        badge.textContent = parseInt(badge.textContent) + 1
    }

    else if (data.type == 'message') {
        var messages = document.getElementById('chatMessages')
        var message = document.createElement('li')
        if (data.message.sender == 'admin') {
            message.innerHTML = `
                        <p>Сообщение от администратора</p>
                        <p>${data.message.text}</p>
                        <p>Время отправки: ${data.message.created_at}</p>`
        }
        else {
            message.innerHTML = `
                        <p>Сообщение от пользователя</p>
                        <p>${data.message.text}</p>
                        <p>Время отправки: ${data.message.created_at}</p>`
        }

        messages.appendChild(message)
    }

    else if (data.type == 'openChat') {
        var messages = document.getElementById('chatMessages')
        data.history.forEach(msg => {
            var message = document.createElement('li')
            if (msg.sender == 'admin') {
                message.innerHTML = `
                        <p>Сообщение от администратора</p>
                        <p>${msg.text}</p>
                        <p>Время отправки: ${msg.created_at}</p>`
            }
            else {
                message.innerHTML = `
                        <p>Сообщение от пользователя</p>
                        <p>${msg.text}</p>
                        <p>Время отправки: ${msg.created_at}</p>`
            }
            messages.appendChild(message)
        });
    }

    else if (data.type == 'newUser') {
        console.log(data.user)
        var chats = document.getElementById('chatList')
        var chat = document.createElement('li')
        chat.className = 'chat-item'
        chat.id = 'chat_' + data.user.user_id
        chat.onclick = () => openChat(data.user.user_id, data.user.first_name, data.user.last_name)
        var content = document.createTextNode(data.user.first_name + ' ' + data.user.last_name)
        chat.appendChild(content)
        chats.appendChild(chat)
    }
};

function openChat(chatId, firstName, lastName) {
    ws.send(JSON.stringify({ 'type': 'openChat', 'user_id': chatId }))
    document.getElementById('chatHeader').textContent = firstName + ' ' + lastName;
    document.getElementById('chatWindow').style.display = 'block';
    document.getElementById('chatMessages').innerHTML = '';
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const val_message = input.value;
    ws.send(JSON.stringify({ 'type': 'message', 'message': val_message }));
    input.value = '';
}
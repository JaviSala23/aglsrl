document.addEventListener('DOMContentLoaded', function() {
    const chatToggle = document.getElementById('chatToggle');
    const chatPanel = document.getElementById('chatPanel');
    const chatClose = document.getElementById('chatClose');
    const chatRooms = document.getElementById('chatRooms');
    const chatMessages = document.getElementById('chatMessages');
    const chatMessageList = document.getElementById('chatMessageList');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    let currentRoom = null;
    let pollInterval = null;

    function togglePanel() {
        chatPanel.classList.toggle('d-none');
    }

    chatToggle && chatToggle.addEventListener('click', togglePanel);
    chatClose && chatClose.addEventListener('click', togglePanel);

    function renderRooms(rooms) {
        chatRooms.innerHTML = '';
        if (!rooms.length) {
            chatRooms.innerHTML = '<small class="text-muted">No tienes salas activas.</small>';
            return;
        }
        rooms.forEach(r => {
            const div = document.createElement('div');
            div.className = 'chat-room p-2 border-bottom';
            div.innerHTML = `<div class="d-flex justify-content-between align-items-center">
                                <div>${r.nombre || 'Sala ' + r.id}</div>
                                <div><small class="text-muted">${r.miembros.join(', ')}</small></div>
                             </div>`;
            div.addEventListener('click', () => openRoom(r.id));
            chatRooms.appendChild(div);
        });
    }

    function openRoom(roomId) {
        currentRoom = roomId;
        chatMessages.classList.remove('d-none');
        chatMessageList.innerHTML = '<small class="text-muted">Cargando mensajes...</small>';
        fetch(`/agenda/chat/${roomId}/messages/`, {credentials: 'same-origin'})
            .then(r => r.json())
            .then(data => {
                chatMessageList.innerHTML = '';
                data.messages.forEach(m => {
                    const el = document.createElement('div');
                    el.className = 'mb-2';
                    el.setAttribute('data-message-id', m.id);
                    el.innerHTML = `<strong>${m.usuario}:</strong> ${m.mensaje} <br><small class="text-muted">${new Date(m.fecha).toLocaleString()}</small>`;
                    chatMessageList.appendChild(el);
                });
                chatMessageList.scrollTop = chatMessageList.scrollHeight;

                // Start polling
                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(() => pollMessages(roomId), 3000);
                // Marcar como leídos los mensajes visibles
                markVisibleAsRead();
                // Mostrar botones de agregar/cerrar según si la sala está abierta y el usuario es creador
                // Para simplificar, siempre mostrar el botón de agregar; el backend validará permisos.
                const addBtn = document.getElementById('chatAddMembersBtn');
                const closeBtn = document.getElementById('chatCloseRoomBtn');
                if (addBtn) addBtn.style.display = 'inline-block';
                if (closeBtn) closeBtn.style.display = 'inline-block';
            }).catch(e => {
                chatMessageList.innerHTML = '<small class="text-danger">Error cargando mensajes</small>';
            });
    }

    function pollMessages(roomId) {
        if (!roomId) return;
        fetch(`/agenda/chat/${roomId}/messages/`, {credentials: 'same-origin'})
            .then(r => r.json())
            .then(data => {
                chatMessageList.innerHTML = '';
                data.messages.forEach(m => {
                    const el = document.createElement('div');
                    el.className = 'mb-2';
                    el.setAttribute('data-message-id', m.id);
                    el.innerHTML = `<strong>${m.usuario}:</strong> ${m.mensaje} <br><small class="text-muted">${new Date(m.fecha).toLocaleString()}</small>`;
                    chatMessageList.appendChild(el);
                });
                chatMessageList.scrollTop = chatMessageList.scrollHeight;
                // Marcar visibles como leídos
                markVisibleAsRead();
            }).catch(e => {});
    }

    function markVisibleAsRead() {
        // obtener ids de mensajes en el DOM
        const ids = Array.from(chatMessageList.querySelectorAll('[data-message-id]')).map(el => el.getAttribute('data-message-id'));
        if (!ids.length) return;
        const form = new URLSearchParams();
        form.append('message_ids', ids.join(','));
        fetch('/agenda/chat/mark_read/', {
            method: 'POST',
            body: form,
            credentials: 'same-origin',
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).then(r => r.json()).then(data => {
            // actualizar contador inmediatamente
            updateUnread();
        }).catch(e => {});
    }

    chatSend && chatSend.addEventListener('click', () => {
        if (!currentRoom) return;
        const text = chatInput.value.trim();
        if (!text) return;
        const form = new URLSearchParams();
        form.append('mensaje', text);
        fetch(`/agenda/chat/${currentRoom}/send/`, {
            method: 'POST',
            body: form,
            credentials: 'same-origin',
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).then(r => r.json())
        .then(data => {
            chatInput.value = '';
            pollMessages(currentRoom);
        }).catch(e => console.error(e));
    });

    // Búsqueda de usuarios para crear sala privada
    const chatUserSearch = document.getElementById('chatUserSearch');
    const chatSearchResults = document.getElementById('chatSearchResults');
    const chatAddMembersArea = document.getElementById('chatAddMembersArea');
    const chatAddMembersList = document.getElementById('chatAddMembersList');
    const chatConfirmAddMembers = document.getElementById('chatConfirmAddMembers');
    const chatCancelAddMembers = document.getElementById('chatCancelAddMembers');

    let searchTimeout = null;
    if (chatUserSearch) {
        chatUserSearch.addEventListener('input', () => {
            const q = chatUserSearch.value.trim();
            if (searchTimeout) clearTimeout(searchTimeout);
            if (!q) { chatSearchResults.innerHTML = ''; return; }
            searchTimeout = setTimeout(() => {
                fetch(`/agenda/chat/search_users/?q=${encodeURIComponent(q)}`, {credentials: 'same-origin'})
                    .then(r => r.json())
                    .then(data => {
                        chatSearchResults.innerHTML = '';
                        data.users.forEach(u => {
                            const el = document.createElement('div');
                            el.className = 'p-2 border-bottom';
                            el.innerHTML = `<div class="d-flex justify-content-between align-items-center">
                                                <div>${u.nombre} <small class="text-muted">@${u.username}</small></div>
                                                <div>
                                                    <button class="btn btn-sm btn-primary btn-create-room" data-id="${u.id}">Abrir</button>
                                                    <button class="btn btn-sm btn-outline-secondary btn-select-user" data-id="${u.id}" data-nombre="${u.nombre}">Seleccionar</button>
                                                </div>
                                            </div>`;
                            chatSearchResults.appendChild(el);
                        });

                        // attach listeners
                        document.querySelectorAll('.btn-create-room').forEach(btn => {
                            btn.addEventListener('click', (e) => {
                                const otherId = btn.getAttribute('data-id');
                                const form = new URLSearchParams();
                                form.append('other_user_id', otherId);
                                fetch('/agenda/chat/create_private/', {
                                    method: 'POST',
                                    body: form,
                                    credentials: 'same-origin',
                                    headers: {'X-CSRFToken': getCookie('csrftoken')}
                                }).then(r => r.json()).then(data => {
                                    if (data.room_id) {
                                        chatUserSearch.value = '';
                                        chatSearchResults.innerHTML = '';
                                        loadRooms();
                                        openRoom(data.room_id);
                                    }
                                }).catch(e => console.error(e));
                            });
                        });

                        // attach listeners for selecting users to add
                        document.querySelectorAll('.btn-select-user').forEach(btn => {
                            btn.addEventListener('click', (e) => {
                                const uid = btn.getAttribute('data-id');
                                const nombre = btn.getAttribute('data-nombre');
                                // add to selection list
                                const existing = chatAddMembersList.querySelector('[data-id="' + uid + '"]');
                                if (existing) return;
                                const row = document.createElement('div');
                                row.setAttribute('data-id', uid);
                                row.className = 'p-1 border-bottom d-flex justify-content-between align-items-center';
                                row.innerHTML = `<div>${nombre}</div><div><button class="btn btn-sm btn-outline-danger btn-remove-selected">Quitar</button></div>`;
                                chatAddMembersList.appendChild(row);
                                // attach remove
                                row.querySelector('.btn-remove-selected').addEventListener('click', () => row.remove());
                                // show add area
                                if (chatAddMembersArea) chatAddMembersArea.classList.remove('d-none');
                            });
                        });
                    }).catch(e => { chatSearchResults.innerHTML = '<small class="text-danger">Error buscando usuarios</small>'; });
            }, 350);
        });
    }

    // Abrir el área de agregar miembros
    const chatAddMembersBtn = document.getElementById('chatAddMembersBtn');
    if (chatAddMembersBtn) {
        chatAddMembersBtn.addEventListener('click', () => {
            if (!currentRoom) return alert('Abre una sala primero');
            if (chatAddMembersArea) chatAddMembersArea.classList.toggle('d-none');
        });
    }

    // Cancelar agregar
    if (chatCancelAddMembers) chatCancelAddMembers.addEventListener('click', () => {
        chatAddMembersList.innerHTML = '';
        chatAddMembersArea.classList.add('d-none');
    });

    // Confirmar agregar
    if (chatConfirmAddMembers) chatConfirmAddMembers.addEventListener('click', () => {
        if (!currentRoom) return alert('Abre una sala primero');
        const ids = Array.from(chatAddMembersList.querySelectorAll('[data-id]')).map(el => el.getAttribute('data-id'));
        if (!ids.length) return alert('Selecciona usuarios para agregar');
        const form = new URLSearchParams();
        form.append('user_ids', ids.join(','));
        fetch(`/agenda/chat/${currentRoom}/add_members/`, {
            method: 'POST',
            body: form,
            credentials: 'same-origin',
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).then(r => r.json()).then(data => {
            // limpiar UI
            chatAddMembersList.innerHTML = '';
            chatAddMembersArea.classList.add('d-none');
            chatSearchResults.innerHTML = '';
            chatUserSearch.value = '';
            // recargar salas
            loadRooms();
        }).catch(e => console.error(e));
    });

    // Cerrar sala
    const chatCloseRoomBtn = document.getElementById('chatCloseRoomBtn');
    if (chatCloseRoomBtn) {
        chatCloseRoomBtn.addEventListener('click', () => {
            if (!currentRoom) return alert('Abre una sala primero');
            if (!confirm('¿Cerrar esta sala? Esto la desactivará para todos.')) return;
            fetch(`/agenda/chat/${currentRoom}/close/`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'X-CSRFToken': getCookie('csrftoken')}
            }).then(r => r.json()).then(data => {
                if (data.closed) {
                    // ocultar panel y recargar salas
                    chatMessages.classList.add('d-none');
                    currentRoom = null;
                    loadRooms();
                } else {
                    alert('No se pudo cerrar la sala');
                }
            }).catch(e => console.error(e));
        });
    }

    function loadRooms() {
        fetch('/agenda/chat/rooms/', {credentials: 'same-origin'})
            .then(r => r.json())
            .then(data => renderRooms(data.rooms))
            .catch(e => { chatRooms.innerHTML = '<small class="text-danger">Error cargando salas</small>'; });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Inicializar
    loadRooms();
    // Poll para contar mensajes sin leer
    const unreadBadge = document.getElementById('chat-unread-count');
    function updateUnread() {
        fetch('/agenda/chat/unread_count/', {credentials: 'same-origin'})
            .then(r => r.json())
            .then(data => {
                const n = parseInt(data.unread_count || 0, 10);
                if (n > 0) {
                    unreadBadge.style.display = 'inline-block';
                    unreadBadge.textContent = n;
                } else {
                    unreadBadge.style.display = 'none';
                }
            }).catch(e => {});
    }

    // Llamar periódicamente
    updateUnread();
    setInterval(updateUnread, 5000);
});
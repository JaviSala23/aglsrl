from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from .models import ChatRoom, ChatMembership, ChatMessage


class ChatMarkReadTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.u1 = User.objects.create_user(username='u1', password='pass')
        self.u2 = User.objects.create_user(username='u2', password='pass')

        # crear sala privada y miembros
        self.room = ChatRoom.objects.create(nombre='private-test', es_grupal=False, creado_por=self.u1)
        ChatMembership.objects.create(sala=self.room, usuario=self.u1)
        ChatMembership.objects.create(sala=self.room, usuario=self.u2)

        # crear mensajes como u1 (no leidos por u2)
        ChatMessage.objects.create(sala=self.room, usuario=self.u1, mensaje='mensaje 1')
        ChatMessage.objects.create(sala=self.room, usuario=self.u1, mensaje='mensaje 2')

    def test_mark_visible_messages_as_read(self):
        client = Client()
        client.force_login(self.u2)

        # comprobar contador inicial
        resp = client.get('/agenda/chat/unread_count/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('unread_count'), 2)

        # marcar los mensajes como leidos (simula lo que hace el cliente tras render)
        msgs = ChatMessage.objects.filter(sala=self.room)
        ids = ','.join(str(m.id) for m in msgs)
        resp2 = client.post('/agenda/chat/mark_read/', {'message_ids': ids})
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json().get('marked'), 2)

        # comprobar contador final
        resp3 = client.get('/agenda/chat/unread_count/')
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp3.json().get('unread_count'), 0)

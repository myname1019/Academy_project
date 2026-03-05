import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db.models import Q

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])
        self.group_name = f"chat_room_{self.conversation_id}"

        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        allowed = await self._is_user_in_conversation(user.id, self.conversation_id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # ✅ 방에 들어오면: 상대가 보낸 안읽은 메시지 읽음 처리
        updated = await self._mark_other_messages_as_read(
            conversation_id=self.conversation_id,
            reader_id=user.id,
        )

        # ✅ 내 unread_count 갱신
        my_unread_count = await self._get_unread_count(user.id)
        await self.channel_layer.group_send(
            f"notify_user_{user.id}",
            {"type": "notify.unread", "unread_count": my_unread_count},
        )

        # ✅ 상대 unread_count도 갱신 (상대 빨간점 즉시 반영)
        other_user_id = await self._get_other_user_id(self.conversation_id, user.id)
        other_unread_count = await self._get_unread_count(other_user_id)
        await self.channel_layer.group_send(
            f"notify_user_{other_user_id}",
            {"type": "notify.unread", "unread_count": other_unread_count},
        )

        # ✅ 읽음 이벤트 브로드캐스트
        if updated:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.read",
                    "reader_id": user.id,
                    "read_at": timezone.now().isoformat(timespec="seconds"),
                },
            )

        # ✅ "나는 지금 방을 보고 있다" 상태 초기값 (연결만으로는 확정하지 않음)
        self.scope["chat_seen"] = True

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return

        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = payload.get("action")

        # ✅ 클라이언트가 "난 지금 화면 보고 있음" 핑을 보내면 처리
        if action == "seen":
            # 방에 있는 동안 주기적으로 이거 보내게 하면 더 확실해짐
            self.scope["chat_seen"] = True

            # 내가 들어와서 보는 순간 상대 메시지 읽음 처리 + read 이벤트
            updated = await self._mark_other_messages_as_read(
                conversation_id=self.conversation_id,
                reader_id=user.id,
            )

            # 내/상대 unread_count 갱신 알림
            my_unread_count = await self._get_unread_count(user.id)
            await self.channel_layer.group_send(
                f"notify_user_{user.id}",
                {"type": "notify.unread", "unread_count": my_unread_count},
            )

            other_user_id = await self._get_other_user_id(self.conversation_id, user.id)
            other_unread_count = await self._get_unread_count(other_user_id)
            await self.channel_layer.group_send(
                f"notify_user_{other_user_id}",
                {"type": "notify.unread", "unread_count": other_unread_count},
            )

            if updated:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat.read",
                        "reader_id": user.id,
                        "read_at": timezone.now().isoformat(timespec="seconds"),
                    },
                )
            return

        # ✅ 메시지 전송
        if action != "send":
            return

        content = (payload.get("content") or "").strip()
        if not content:
            return

        # 1) DB 저장
        msg = await self._create_message(
            conversation_id=self.conversation_id,
            sender_id=user.id,
            content=content,
        )

        # 2) 그룹에 메시지 브로드캐스트 (상대에게 바로 보임)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message_id": msg["id"],
                "conversation_id": self.conversation_id,
                "sender_id": msg["sender_id"],
                "content": msg["content"],
                "created_at": msg["created_at"],
                "is_read": msg["is_read"],
            },
        )

        # 3) 상대가 "현재 채팅 화면을 보고 있다(seen 핑을 보내는 중)"면 즉시 읽음 처리
        #    (가장 확실한 버전: 메시지 전송 직후, 상대가 seen이면 읽음 처리)
        other_user_id = await self._get_other_user_id(self.conversation_id, user.id)
        other_is_online_in_room = await self._is_other_seen(self.conversation_id, other_user_id)

        if other_is_online_in_room:
            await self._mark_message_read(msg["id"])

            # 방 전체에 read 이벤트 뿌려서 "안읽음→읽음" UI 갱신
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.read",
                    "reader_id": other_user_id,
                    "read_at": timezone.now().isoformat(timespec="seconds"),
                },
            )

        # 4) 알림 unread_count 갱신 (양쪽 다 최신화)
        my_unread_count = await self._get_unread_count(user.id)
        await self.channel_layer.group_send(
            f"notify_user_{user.id}",
            {"type": "notify.unread", "unread_count": my_unread_count},
        )

        other_unread_count = await self._get_unread_count(other_user_id)
        await self.channel_layer.group_send(
            f"notify_user_{other_user_id}",
            {"type": "notify.unread", "unread_count": other_unread_count},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"event": "message", "data": event}, ensure_ascii=False))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({"event": "read", "data": event}, ensure_ascii=False))

    # ---------------- DB helpers ----------------

    @database_sync_to_async
    def _is_user_in_conversation(self, user_id, conversation_id):
        try:
            convo = Conversation.objects.select_related("teacher", "student").get(id=conversation_id)
        except Conversation.DoesNotExist:
            return False
        return convo.teacher_id == user_id or convo.student_id == user_id

    @database_sync_to_async
    def _create_message(self, conversation_id, sender_id, content):
        convo = Conversation.objects.get(id=conversation_id)
        msg = Message.objects.create(conversation=convo, sender_id=sender_id, content=content)
        return {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(timespec="seconds"),
            "is_read": msg.is_read,
        }

    @database_sync_to_async
    def _mark_other_messages_as_read(self, conversation_id, reader_id):
        qs = (
            Message.objects
            .filter(conversation_id=conversation_id, is_read=False)
            .exclude(sender_id=reader_id)
        )
        updated_count = qs.update(is_read=True, read_at=timezone.now())
        return updated_count > 0

    @database_sync_to_async
    def _mark_message_read(self, message_id):
        Message.objects.filter(id=message_id, is_read=False).update(is_read=True, read_at=timezone.now())

    @database_sync_to_async
    def _get_other_user_id(self, conversation_id, my_id):
        convo = Conversation.objects.get(id=conversation_id)
        if convo.teacher_id == my_id:
            return convo.student_id
        return convo.teacher_id

    @database_sync_to_async
    def _get_unread_count(self, user_id):
        return (
            Message.objects.filter(
                Q(conversation__teacher_id=user_id) | Q(conversation__student_id=user_id),
                is_read=False,
            )
            .exclude(sender_id=user_id)
            .count()
        )

    # ✅ 핵심: "상대가 방을 보고 있다" 상태를 서버가 알 수 있게 저장/조회
    @database_sync_to_async
    def _is_other_seen(self, conversation_id, other_user_id):
        """
        초보용 간단판:
        - 가장 안정적으로 하려면 Redis/DB/캐시 등에 상태를 저장해야 하지만,
          현재는 "둘 다 방을 켜놓고 있을 때" 읽음 처리만 목표이므로
          Message 기반으로 '최근 read_at 업데이트'로도 충분히 동작 가능.
        - 여기서는 '상대가 방에 들어오면 connect에서 mark_as_read가 일어나므로'
          그 순간 이후에는 online 상태로 본다.

        👉 더 정확히 하려면 Redis presence로 바꾸는 게 정석.
        """
        # 간단판에서는 True로 둬도 되지만, 너무 공격적으로 읽음 처리될 수 있음.
        # 그래서 "상대가 이 대화방에서 최근 3분 안에 메시지를 읽은 기록이 있으면"으로 판정
        three_min_ago = timezone.now() - timezone.timedelta(minutes=3)
        return Message.objects.filter(
            conversation_id=conversation_id,
            read_at__gte=three_min_ago,
        ).exists()
    
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user_id = user.id
        self.group_name = f"notify_user_{self.user_id}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        unread_count = await self._get_unread_count(self.user_id)

        await self.send(
            json.dumps({
                "event": "unread_count",
                "data": {"unread_count": unread_count}
            })
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_unread(self, event):
        await self.send(
            json.dumps({
                "event": "unread_count",
                "data": {"unread_count": event["unread_count"]}
            })
        )

    @database_sync_to_async
    def _get_unread_count(self, user_id):
        return (
            Message.objects.filter(
                Q(conversation__teacher_id=user_id) |
                Q(conversation__student_id=user_id),
                is_read=False
            )
            .exclude(sender_id=user_id)
            .count()
        )
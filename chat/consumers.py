# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.utils import timezone
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

        # [수정 포인트] 입장 시 읽음 처리 후 즉시 그룹에 알림
        read_ids = await self._mark_other_messages_as_read_and_get_ids(
            conversation_id=self.conversation_id,
            reader_id=user.id,
        )

        # 내 안읽음 숫자 갱신 (기존 기능 유지)
        my_unread_count = await self._get_unread_count(user.id)
        await self.channel_layer.group_send(
            f"notify_user_{user.id}",
            {"type": "notify.unread", "unread_count": my_unread_count},
        )

        if read_ids:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.read",
                    "reader_id": user.id,
                    "read_at": timezone.now().isoformat(timespec="seconds"),
                    "message_ids": read_ids, # 이 ID들이 JS로 전달되어야 함
                },
            )

    async def disconnect(self, close_code):
        # 그룹에서 빠지기
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # 로그인 확인
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return
        if not text_data:
            return

        # JSON 파싱
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = payload.get("action")

        # (중요) seen 핑: “난 지금 화면 보고 있음” -> 미읽음 읽음 처리 + read 이벤트
        if action == "seen":
            read_ids = await self._mark_other_messages_as_read_and_get_ids(
                conversation_id=self.conversation_id,
                reader_id=user.id,
            )

            # 내 unread_count 갱신
            my_unread_count = await self._get_unread_count(user.id)
            await self.channel_layer.group_send(
                f"notify_user_{user.id}",
                {"type": "notify.unread", "unread_count": my_unread_count},
            )

            # 읽은 메시지가 있으면 read 이벤트 브로드캐스트
            if read_ids:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat.read",
                        "reader_id": user.id,
                        "read_at": timezone.now().isoformat(timespec="seconds"),
                        "message_ids": read_ids,
                    },
                )
            return

        # send만 처리
        if action != "send":
            return

        content = (payload.get("content") or "").strip()
        if not content:
            return

        # DB 저장
        msg = await self._create_message(
            conversation_id=self.conversation_id,
            sender_id=user.id,
            content=content,
        )

        # room 전체에 message 이벤트 브로드캐스트
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

        # 상대 unread_count도 갱신해서 빨간점 즉시 반영
        other_user_id = await self._get_other_user_id(self.conversation_id, user.id)
        other_unread_count = await self._get_unread_count(other_user_id)
        await self.channel_layer.group_send(
            f"notify_user_{other_user_id}",
            {"type": "notify.unread", "unread_count": other_unread_count},
        )

    # ===== room 이벤트 핸들러 (type 값과 함수명이 매칭됨) =====

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"event": "message", "data": event}, ensure_ascii=False))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({"event": "read", "data": event}, ensure_ascii=False))

    # ===== DB helper =====

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
    def _mark_other_messages_as_read_and_get_ids(self, conversation_id, reader_id):
        # 내가 reader이고, 상대가 보낸 것만 읽음 처리
        qs = (
            Message.objects
            .filter(conversation_id=conversation_id, is_read=False)
            .exclude(sender_id=reader_id)
            .order_by("id")
        )
        ids = list(qs.values_list("id", flat=True))
        if ids:
            qs.update(is_read=True, read_at=timezone.now())
        return ids

    @database_sync_to_async
    def _get_other_user_id(self, conversation_id, my_id):
        convo = Conversation.objects.get(id=conversation_id)
        return convo.student_id if convo.teacher_id == my_id else convo.teacher_id

    @database_sync_to_async
    def _get_unread_count(self, user_id):
        # 내가 속한 대화방에서 sender != 나, is_read=False인 것만 카운트
        return (
            Message.objects.filter(
                Q(conversation__teacher_id=user_id) | Q(conversation__student_id=user_id),
                is_read=False,
            )
            .exclude(sender_id=user_id)
            .count()
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    알림 전용 WebSocket
    - ws/notify/ 로 연결
    - notify_user_<user_id> 그룹으로 unread_count 실시간 푸시
    """

    async def connect(self):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user_id = user.id
        self.group_name = f"notify_user_{self.user_id}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # 연결 즉시 1회 unread_count 보내서 초기 동기화
        unread_count = await self._get_unread_count(self.user_id)
        await self.send(
            text_data=json.dumps(
                {"event": "unread_count", "data": {"unread_count": unread_count}},
                ensure_ascii=False,
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_unread(self, event):
        # ChatConsumer에서 group_send한 unread_count를 그대로 전달
        await self.send(
            text_data=json.dumps(
                {"event": "unread_count", "data": {"unread_count": event["unread_count"]}},
                ensure_ascii=False,
            )
        )

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
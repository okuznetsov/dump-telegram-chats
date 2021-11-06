from django.contrib import admin

from web.models import Chat, User, Message


class ChatAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_filter = ["chat_type"]
    list_display = ["id", "title", "date", "last_message_date", "disabled", "chat_type"]


admin.site.register(Chat, ChatAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "username"]


admin.site.register(User, UserAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "chat", "user", "__str__", "date"]
    list_filter = ["user", "chat"]


admin.site.register(Message, MessageAdmin)

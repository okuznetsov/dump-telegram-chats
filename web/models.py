from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True, default=1)
    name = models.TextField(default=None, blank=True, null=True)
    username = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        if self.name:
            return f'{self.name} #{self.id}'
        return str(self.id)


class Chat(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    title = models.TextField()
    date = models.DateTimeField()
    udate = models.DateTimeField(auto_now=True, auto_created=True, blank=True, null=True)
    last_message_date = models.DateTimeField(blank=True, null=True)
    disabled = models.BooleanField(default=False)
    chat_type = models.CharField(max_length=255, blank=True, null=True)
    migrated_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    text = models.TextField(default=None, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    original_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text
        # return self.text[:50] + "..."

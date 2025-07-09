from django.db import models
from django.contrib.auth.models import User

class Doc(models.Model):
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    size = models.FloatField(null=True, blank=True, help_text="Размер файла в КБ")
    external_doc_id = models.CharField(max_length=255, null=True, blank=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.image:
            self.file_path = self.image.name
            self.size = self.image.size / 1024
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Doc #{self.id} ({self.file_path})"

class UserToDocs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.user.username} → Doc #{self.doc.id}"

    def __str__(self):
        return f"{self.username} → {self.doc_id}"

class Price(models.Model):
    file_type = models.CharField(max_length=10)
    price = models.FloatField(help_text="Цена за 1 КБ")

    def __str__(self):
        return f"{self.file_type}: {self.price}₽/КБ"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)

    def __str__(self):
        return f"Order by {self.user.username} | Paid: {self.payment}"

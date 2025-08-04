from django.db import models


class Estado(models.Model):
    name = models.CharField("nome",max_length=100)
    color = models.CharField("cor",max_length=8,default="#FF0000")
    colorHTML = models.CharField("cor html",max_length=50,default="color:#FF0000;")
    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.name

class OS(models.Model):
    name = models.CharField("nome",max_length=100)
    description = models.CharField("Descrição",max_length=500)
    state = models.ForeignKey(Estado, on_delete=models.DO_NOTHING)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'OS'
        verbose_name_plural = 'OS'

    def __str__(self):
        return self.name


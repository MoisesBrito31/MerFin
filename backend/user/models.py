from django.db import models
from stdimage import StdImageField
from django.contrib.auth.models import AbstractUser
from django.db.models import BigAutoField

class Usuario(AbstractUser):
    id = BigAutoField('id',primary_key=True, unique=True)
    email = models.EmailField('E-mail', unique=True)
    fone = models.CharField('Telefone', max_length=15)
    is_staff = models.BooleanField('Membro da equipe', default=True)
    email_checked = models.BooleanField('E-mail Aprovado',default=False)
    departamento = models.CharField('Departamento',default="",max_length=30)
    avatar = StdImageField('Avatar',upload_to='avatares',variations={
        'menu': {'width':100,'height':100, 'crop': True},
        'post': {'width':200,'height':200, 'crop': True}
    },delete_orphans=True,default="")
    alertasNovos = models.IntegerField('alertas não lidos',default=0)

    def __str__(self):
        return self.username
